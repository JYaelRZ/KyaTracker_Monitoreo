"""
Flask backend for KyaTracker Monitoreo y Custodia Digital
"""
import os, uuid, datetime, json, csv, io
from flask import Flask, render_template, request, jsonify, send_file, Response
from sqlalchemy import func
from database.connection import SessionLocal
from database.models import MonitoringService
from utils.exporter import export_data_to_excel_file
from utils.ticket_generator import generate_monitoring_ticket_pdf
from utils.invoice_generator import generate_consolidated_invoice

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clients', methods=['GET'])
def get_clients():
    with SessionLocal() as db:
        clients = db.query(MonitoringService.client).distinct().all()
        return jsonify([c[0] for c in clients])

@app.route('/api/services', methods=['GET'])
def get_services():
    client = request.args.get('client', '')
    with SessionLocal() as db:
        q = db.query(MonitoringService).order_by(MonitoringService.created_at.desc())
        if client:
            q = q.filter(MonitoringService.client == client)
        services = q.all()
        result = []
        for s in services:
            result.append({
                'id': s.id,
                'unit': s.unit,
                'operator': s.operator,
                'client': s.client,
                'origin': s.origin,
                'destination': s.destination,
                'start_time': s.start_time.strftime('%d/%m/%Y %I:%M %p') if s.start_time else '',
                'arrival_time': s.arrival_time.strftime('%d/%m/%Y %I:%M %p') if s.arrival_time else None,
                'hourly_rate': s.hourly_rate,
                'billed_minutes': s.billed_minutes,
                'total_cost': s.total_cost,
                'financial_status': s.financial_status
            })
        return jsonify(result)

@app.route('/api/client_stats', methods=['GET'])
def client_stats():
    client = request.args.get('client', '')
    with SessionLocal() as db:
        q = db.query(MonitoringService)
        if client:
            q = q.filter(MonitoringService.client == client)
        services = q.all()

        # Destination frequency
        dest_freq = {}
        total_cost = 0.0
        active = 0
        completed = 0
        total_minutes = 0

        for s in services:
            dest_freq[s.destination] = dest_freq.get(s.destination, 0) + 1
            if s.total_cost:
                total_cost += s.total_cost
            if s.arrival_time is None:
                active += 1
            else:
                completed += 1
            if s.billed_minutes:
                total_minutes += s.billed_minutes

        # Sort destinations by frequency
        sorted_dests = sorted(dest_freq.items(), key=lambda x: x[1], reverse=True)

        return jsonify({
            'destinations': [{'name': d[0], 'count': d[1]} for d in sorted_dests],
            'total_services': len(services),
            'active': active,
            'completed': completed,
            'total_revenue': round(total_cost, 2),
            'total_minutes': total_minutes
        })

@app.route('/api/all_stats', methods=['GET'])
def all_stats():
    """Stats summary for each client"""
    with SessionLocal() as db:
        services = db.query(MonitoringService).all()
        clients = {}
        for s in services:
            if s.client not in clients:
                clients[s.client] = {'active': 0, 'completed': 0, 'revenue': 0.0, 'services': 0}
            clients[s.client]['services'] += 1
            if s.arrival_time is None:
                clients[s.client]['active'] += 1
            else:
                clients[s.client]['completed'] += 1
            if s.total_cost:
                clients[s.client]['revenue'] += s.total_cost
        
        result = []
        for name, data in clients.items():
            data['name'] = name
            data['revenue'] = round(data['revenue'], 2)
            result.append(data)
        return jsonify(sorted(result, key=lambda x: x['name']))

@app.route('/api/global_stats', methods=['GET'])
def global_stats():
    """Global overview statistics for the main dashboard"""
    with SessionLocal() as db:
        services = db.query(MonitoringService).all()
        
        total_revenue = sum(s.total_cost for s in services if s.total_cost)
        total_active = sum(1 for s in services if not s.arrival_time)
        total_completed = sum(1 for s in services if s.arrival_time)
        
        client_stats = {}
        for s in services:
            c = s.client
            if c not in client_stats:
                client_stats[c] = {'revenue': 0, 'active': 0, 'total': 0}
            client_stats[c]['total'] += 1
            if s.total_cost:
                client_stats[c]['revenue'] += s.total_cost
            if not s.arrival_time:
                client_stats[c]['active'] += 1
                
        top_active_client = max(client_stats.items(), key=lambda x: x[1]['active'], default=None)
        
        top_revenue_clients = sorted(
            [{'name': k, 'revenue': v['revenue']} for k, v in client_stats.items()],
            key=lambda x: x['revenue'], reverse=True
        )[:5]

        return jsonify({
            'total_clients': len(client_stats),
            'total_revenue': total_revenue,
            'total_active': total_active,
            'total_completed': total_completed,
            'top_active_client': top_active_client[0] if top_active_client and top_active_client[1]['active'] > 0 else 'Ninguno',
            'top_active_count': top_active_client[1]['active'] if top_active_client else 0,
            'top_revenue_clients': top_revenue_clients
        })

@app.route('/api/services', methods=['POST'])
def create_service():
    data = request.json
    # Parse manual datetime with AM/PM
    try:
        start_dt = datetime.datetime.strptime(data['start_time'], '%d/%m/%Y %I:%M %p')
        start_dt = start_dt.replace(tzinfo=datetime.timezone.utc)
    except (ValueError, KeyError) as e:
        return jsonify({'error': f'Formato de fecha/hora inválido: {e}'}), 400

    arrival_dt = None
    if data.get('arrival_time'):
        try:
            arrival_dt = datetime.datetime.strptime(data['arrival_time'], '%d/%m/%Y %I:%M %p')
            arrival_dt = arrival_dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de fecha/hora llegada inválido: {e}'}), 400

    try:
        with SessionLocal() as db:
            s = MonitoringService(
                id=str(uuid.uuid4()),
                unit=data['unit'],
                operator=data['operator'],
                client=data['client'],
                origin=data['origin'],
                destination=data['destination'],
                start_time=start_dt,
                arrival_time=arrival_dt,
                hourly_rate=float(data['hourly_rate']),
                financial_status=data.get('financial_status', 'En proceso de facturación')
            )
            db.add(s)
            db.commit()
            db.refresh(s)
            return jsonify({'id': s.id, 'message': 'Servicio registrado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': f'ERROR REAL: {str(e)}'}), 500

@app.route('/api/services/<service_id>', methods=['PUT'])
def update_service(service_id):
    data = request.json
    with SessionLocal() as db:
        s = db.query(MonitoringService).filter(MonitoringService.id == service_id).first()
        if not s:
            return jsonify({'error': 'Servicio no encontrado'}), 404
        
        for field in ['unit', 'operator', 'client', 'origin', 'destination', 'financial_status']:
            if field in data:
                setattr(s, field, data[field])
        if 'hourly_rate' in data:
            s.hourly_rate = float(data['hourly_rate'])
        if 'start_time' in data:
            if data['start_time']:
                s.start_time = datetime.datetime.strptime(data['start_time'], '%d/%m/%Y %I:%M %p').replace(tzinfo=datetime.timezone.utc)
            else:
                s.start_time = None
                
        if 'arrival_time' in data:
            if data['arrival_time']:
                s.arrival_time = datetime.datetime.strptime(data['arrival_time'], '%d/%m/%Y %I:%M %p').replace(tzinfo=datetime.timezone.utc)
            else:
                s.arrival_time = None
        
        db.commit()
        return jsonify({'message': 'Servicio actualizado'})

@app.route('/api/services/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    with SessionLocal() as db:
        s = db.query(MonitoringService).filter(MonitoringService.id == service_id).first()
        if s:
            db.delete(s)
            db.commit()
        return jsonify({'message': 'Eliminado'})

@app.route('/api/ticket/<service_id>', methods=['GET'])
def generate_ticket(service_id):
    with SessionLocal() as db:
        s = db.query(MonitoringService).filter(MonitoringService.id == service_id).first()
        if not s or not s.arrival_time:
            return jsonify({'error': 'Servicio no completado'}), 400
        
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(tmp_fd)
        
        try:
            generate_monitoring_ticket_pdf(
                output_path=tmp_path,
                folio=s.id.split('-')[0].upper(),
                client_name=s.client,
                unit=s.unit,
                origin=s.origin,
                destination=s.destination,
                start_time=s.start_time.strftime('%d/%m/%Y %I:%M %p'),
                arrival_time=s.arrival_time.strftime('%d/%m/%Y %I:%M %p'),
                billed_minutes=s.billed_minutes,
                total_amount=s.total_cost
            )
            with open(tmp_path, 'rb') as f:
                pdf_data = f.read()
            return Response(
                pdf_data, 
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename=Ticket_{s.unit}.pdf'}
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    client = request.args.get('client', '')
    with SessionLocal() as db:
        q = db.query(MonitoringService).order_by(MonitoringService.created_at.desc())
        if client:
            q = q.filter(MonitoringService.client == client)
        services = q.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Unidad', 'Operador', 'Cliente', 'Origen', 'Destino', 'Salida', 'Llegada', 'Minutos', 'Costo', 'Estado Financiero'])
        for s in services:
            writer.writerow([
                s.unit, s.operator, s.client, s.origin, s.destination,
                s.start_time.strftime('%d/%m/%Y %I:%M %p') if s.start_time else '',
                s.arrival_time.strftime('%d/%m/%Y %I:%M %p') if s.arrival_time else 'En Ruta',
                s.billed_minutes or '', s.total_cost or '', s.financial_status
            ])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=Reporte_{client}.csv'}
        )
@app.route('/api/save_file', methods=['POST'])
def save_file():
    """Save a generated file (CSV or Ticket PDF) to a user-specified path"""
    data = request.get_json()
    file_type = data.get('type')        # 'csv' or 'ticket'
    save_path = data.get('path', '')    # directory path
    file_name = data.get('name', '')    # file name without extension
    client = data.get('client', '')
    service_id = data.get('service_id', '')

    if not save_path or not file_name:
        return jsonify({'error': 'Ruta y nombre de archivo son requeridos'}), 400

    # Normalize path
    save_path = os.path.normpath(save_path)
    if not os.path.isdir(save_path):
        try:
            os.makedirs(save_path, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'No se pudo crear la carpeta: {str(e)}'}), 400

    try:
        if file_type == 'csv':
            full_path = os.path.join(save_path, f'{file_name}.csv')
            with SessionLocal() as db:
                q = db.query(MonitoringService).order_by(MonitoringService.created_at.desc())
                if client:
                    q = q.filter(MonitoringService.client == client)
                services = q.all()
                with open(full_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Unidad', 'Operador', 'Cliente', 'Origen', 'Destino', 'Salida', 'Llegada', 'Minutos', 'Costo', 'Estado Financiero'])
                    for s in services:
                        writer.writerow([
                            s.unit, s.operator, s.client, s.origin, s.destination,
                            s.start_time.strftime('%d/%m/%Y %I:%M %p') if s.start_time else '',
                            s.arrival_time.strftime('%d/%m/%Y %I:%M %p') if s.arrival_time else 'En Ruta',
                            s.billed_minutes or '', s.total_cost or '', s.financial_status
                        ])
            return jsonify({'success': True, 'path': full_path})

        elif file_type == 'ticket':
            if not service_id:
                return jsonify({'error': 'ID de servicio requerido'}), 400
            with SessionLocal() as db:
                s = db.query(MonitoringService).filter_by(id=service_id).first()
                if not s:
                    return jsonify({'error': 'Servicio no encontrado'}), 404
                if not s.arrival_time:
                    return jsonify({'error': 'Servicio aún en ruta'}), 400
                # Generate PDF to the specified path
                full_path = os.path.join(save_path, f'{file_name}.pdf')
                generate_monitoring_ticket_pdf(
                    output_path=full_path,
                    service_id=s.id,
                    client_name=s.client,
                    unit=s.unit,
                    origin=s.origin,
                    destination=s.destination,
                    start_time=s.start_time.strftime('%d/%m/%Y %I:%M %p'),
                    arrival_time=s.arrival_time.strftime('%d/%m/%Y %I:%M %p'),
                    billed_minutes=s.billed_minutes,
                    total_amount=s.total_cost
                )
                return jsonify({'success': True, 'path': full_path})
        elif file_type == 'invoice':
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            iva = float(data.get('iva', 16.0))
            
            with SessionLocal() as db:
                q = db.query(MonitoringService).filter(MonitoringService.client == client).order_by(MonitoringService.created_at.desc())
                if start_date_str:
                    sd = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
                    q = q.filter(MonitoringService.start_time >= sd)
                if end_date_str:
                    ed = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc)
                    q = q.filter(MonitoringService.start_time <= ed)
                
                services = q.all()
                if not services:
                    return jsonify({'error': 'No hay servicios en este rango de fechas'}), 404
                    
                date_range_str = f"Del {start_date_str} al {end_date_str}" if start_date_str and end_date_str else "Histórico Completo"
                
                full_path = os.path.join(save_path, f'{file_name}.pdf')
                generate_consolidated_invoice(
                    output_path=full_path,
                    client_name=client,
                    date_range_str=date_range_str,
                    services=services,
                    iva_percentage=iva
                )
                return jsonify({'success': True, 'path': full_path})
        else:
            return jsonify({'error': 'Tipo de archivo no válido'}), 400
    except Exception as e:
        return jsonify({'error': f'Error al guardar: {str(e)}'}), 500

@app.route('/api/invoice_blob', methods=['POST'])
def invoice_blob():
    """Generates the consolidated invoice and returns it as a blob for the frontend native dialog"""
    data = request.get_json()
    client = data.get('client')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    iva = float(data.get('iva', 16.0))
    
    if not client:
        return jsonify({'error': 'Cliente requerido'}), 400
        
    with SessionLocal() as db:
        q = db.query(MonitoringService).filter(MonitoringService.client == client).order_by(MonitoringService.start_time.asc())
        if start_date_str:
            sd = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
            q = q.filter(MonitoringService.start_time >= sd)
        if end_date_str:
            ed = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone.utc)
            q = q.filter(MonitoringService.start_time <= ed)
            
        services = q.all()
        if not services:
            return jsonify({'error': 'No hay servicios en este rango de fechas'}), 404
            
        date_range_str = f"Del {start_date_str} al {end_date_str}" if start_date_str and end_date_str else "Histórico Completo"
        
        # Save to temporary buffer
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(tmp_fd)
        
        try:
            generate_consolidated_invoice(
                output_path=tmp_path,
                client_name=client,
                date_range_str=date_range_str,
                services=services,
                iva_percentage=iva
            )
            with open(tmp_path, 'rb') as f:
                pdf_data = f.read()
            return Response(pdf_data, mimetype='application/pdf')
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    from database.setup_db import init_db
    init_db()
    app.run(debug=True, port=5050)
