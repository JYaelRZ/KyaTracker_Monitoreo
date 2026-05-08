let currentClient=null,allClients=[],allServices=[],topChart=null,bottomChart=null,globalChart=null;
let pendingSaveType=null,pendingSaveServiceId=null;
let currentMapFilter='all', mapZoomLevel=1, mapPanX=0, mapPanY=0, selectedRouteId=null;
document.addEventListener('DOMContentLoaded',()=>{loadClients();loadMexicoMap();});

function showToast(m,t='success'){const c=document.getElementById('toastContainer'),d=document.createElement('div');d.className=`toast ${t}`;d.innerHTML=`${t==='success'?'✅':'❌'} ${m}`;c.appendChild(d);setTimeout(()=>d.remove(),3500);}

async function loadClients(){
    try{
        const month = document.getElementById('globalMonthFilter')?.value || '';
        const url = month ? `/api/all_stats?month=${month}` : '/api/all_stats';
        const r=await fetch(url),d=await r.json();
        allClients=d;renderClientList(d);
        document.getElementById('clientCount').textContent=d.length;
        if(!currentClient) loadGlobalStats();
    }catch(e){console.error(e);}
}

async function loadGlobalStats() {
    try {
        const month = document.getElementById('globalMonthFilter')?.value || '';
        const url = month ? `/api/global_stats?month=${month}` : '/api/global_stats';
        const r = await fetch(url), d = await r.json();
        document.getElementById('globalRevenue').textContent = `$${d.total_revenue.toLocaleString('es-MX', {minimumFractionDigits:2})}`;
        document.getElementById('globalClients').textContent = d.total_clients;
        document.getElementById('globalTotalServices').textContent = d.total_services;
        document.getElementById('globalActive').textContent = d.total_active;
        document.getElementById('globalTopClient').textContent = d.top_client;
        document.getElementById('globalTopClient').title = `${d.top_client_count} rutas en total`;

        if (globalChart) globalChart.destroy();
        const ctx = document.getElementById('globalTopClientsChart').getContext('2d');
        globalChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: d.top_revenue_clients.map(c => c.name),
                datasets: [{
                    data: d.top_revenue_clients.map(c => c.revenue),
                    backgroundColor: ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ec4899'],
                    borderRadius: 6,
                    barThickness: 30
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', callback: value => '$'+value } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    } catch(e) { console.error('Error loading global stats', e); }
}

function filterClients(){
    const q=document.getElementById('clientSearchInput').value.toLowerCase();
    const filtered=allClients.filter(c=>c.name.toLowerCase().includes(q));
    renderClientList(filtered);
}

function renderClientList(clients){
    const list=document.getElementById('clientList');list.innerHTML='';
    const colors=['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6'];
    clients.forEach((c,i)=>{
        const ini=c.name.split(' ').map(w=>w[0]).join('').substring(0,2).toUpperCase();
        const col=colors[i%colors.length],act=currentClient===c.name?'active':'';
        const div=document.createElement('div');div.className=`client-item ${act}`;
        div.onclick=()=>{currentClient=c.name;selectClient(c.name);};
        div.innerHTML=`<div class="client-avatar" style="background:${col}20;color:${col};border:1px solid ${col}40;">${ini}</div><div class="client-info"><h4>${c.name}</h4><p>${c.services} servicios · ${c.active} activos</p></div>`;
        list.appendChild(div);
    });
}

async function selectClient(name){
    currentClient=name;
    document.querySelectorAll('.client-item').forEach(el=>el.classList.remove('active'));
    document.querySelectorAll('.client-item').forEach(el=>{if(el.querySelector('h4')?.textContent===name)el.classList.add('active');});
    
    const btnHome = document.getElementById('btnHome');
    if(btnHome) btnHome.classList.remove('active');
    
    document.getElementById('clientTitle').innerHTML=`Dashboard — <span>${name}</span>`;
    
    const globalDash = document.getElementById('globalDashboard');
    if(globalDash) globalDash.style.display='none';
    
    document.getElementById('dashboardContent').style.display='block';
    await Promise.all([loadClientStats(name),loadClientServices(name)]);
}

function clearClientSelection() {
    currentClient = null;
    document.querySelectorAll('.client-item').forEach(el=>el.classList.remove('active'));
    
    const btnHome = document.getElementById('btnHome');
    if(btnHome) btnHome.classList.add('active');
    
    document.getElementById('clientTitle').innerHTML=`Bienvenido a <span>KyaTracker</span>`;
    
    const globalDash = document.getElementById('globalDashboard');
    if(globalDash) globalDash.style.display='block';
    
    document.getElementById('dashboardContent').style.display='none';
    loadGlobalStats();
}

async function loadClientStats(name){
    try{
        const month = document.getElementById('globalMonthFilter')?.value || '';
        let url = `/api/client_stats?client=${encodeURIComponent(name)}`;
        if(month) url += `&month=${month}`;
        const r=await fetch(url),d=await r.json();
    document.getElementById('statServices').textContent=d.total_services;
    document.getElementById('statActive').textContent=d.active;
    document.getElementById('statRevenue').textContent=`$${d.total_revenue.toLocaleString('es-MX',{minimumFractionDigits:2})}`;
    document.getElementById('statMinutes').textContent=d.total_minutes.toLocaleString();
    renderCharts(d.destinations);}catch(e){console.error(e);}
}

function groupDestinations(destinations){
    const groups={};
    destinations.forEach(d=>{
        let key=d.name.trim();
        const states=["Guanajuato","Jalisco","Nuevo León","Monterrey","Querétaro","Puebla","CDMX","Ciudad de México","Veracruz","Oaxaca","Chiapas","Michoacán","Sonora","Chihuahua","Sinaloa","Tamaulipas","Coahuila","San Luis Potosí","Aguascalientes","Zacatecas","Durango","Nayarit","Colima","Guerrero","Tabasco","Yucatán","Quintana Roo","Campeche","Baja California","Hidalgo","Tlaxcala","Morelos","Estado de México","Edo. de México"];
        let matched=false;
        for(const st of states){if(key.toLowerCase().includes(st.toLowerCase())){key=st;matched=true;break;}}
        if(!matched){
            const cityMap={"León":"Guanajuato","Irapuato":"Guanajuato","Celaya":"Guanajuato","Salamanca":"Guanajuato","Silao":"Guanajuato","Guadalajara":"Jalisco","Zapopan":"Jalisco","Tlaquepaque":"Jalisco","Mérida":"Yucatán","Cancún":"Quintana Roo","Toluca":"Estado de México","Pachuca":"Hidalgo","Morelia":"Michoacán","Hermosillo":"Sonora","Culiacán":"Sinaloa","Mazatlán":"Sinaloa","Saltillo":"Coahuila","Torreón":"Coahuila","Tampico":"Tamaulipas","Reynosa":"Tamaulipas","Villahermosa":"Tabasco","Tuxtla Gutiérrez":"Chiapas","Acapulco":"Guerrero","Tijuana":"Baja California","La Paz":"Baja California Sur","Tepic":"Nayarit"};
            for(const[city,state] of Object.entries(cityMap)){if(key.toLowerCase().includes(city.toLowerCase())){key=state;matched=true;break;}}
        }
        groups[key]=(groups[key]||0)+d.count;
    });
    return Object.entries(groups).map(([name,count])=>({name,count})).sort((a,b)=>b.count-a.count);
}

function renderCharts(destinations){
    if(!destinations||!destinations.length){
        document.getElementById('topChartWrapper').innerHTML='<div class="empty-state"><div class="icon">📊</div><h4>Sin datos</h4></div>';
        document.getElementById('bottomChartWrapper').innerHTML='<div class="empty-state"><div class="icon">📊</div><h4>Sin datos</h4></div>';
        return;
    }
    const grouped=groupDestinations(destinations);
    document.getElementById('topChartWrapper').innerHTML='<canvas id="topChart"></canvas>';
    document.getElementById('bottomChartWrapper').innerHTML='<canvas id="bottomChart"></canvas>';
    if(topChart)topChart.destroy();if(bottomChart)bottomChart.destroy();
    const top5=grouped.slice(0,5),btm5=[...grouped].reverse().slice(0,5);
    topChart=new Chart(document.getElementById('topChart').getContext('2d'),{type:'bar',data:{labels:top5.map(d=>d.name),datasets:[{data:top5.map(d=>d.count),backgroundColor:['#3b82f6','#06b6d4','#8b5cf6','#10b981','#f59e0b'],borderRadius:6,borderSkipped:false,barThickness:22}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#64748b',font:{size:11}}},y:{grid:{display:false},ticks:{color:'#94a3b8',font:{size:11}}}}}});
    bottomChart=new Chart(document.getElementById('bottomChart').getContext('2d'),{type:'bar',data:{labels:btm5.map(d=>d.name),datasets:[{data:btm5.map(d=>d.count),backgroundColor:['#ef4444','#f97316','#eab308','#a855f7','#ec4899'],borderRadius:6,borderSkipped:false,barThickness:22}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.05)'},ticks:{color:'#64748b',font:{size:11}}},y:{grid:{display:false},ticks:{color:'#94a3b8',font:{size:11}}}}}});
}

async function loadClientServices(name){
    try{
        const month = document.getElementById('globalMonthFilter')?.value || '';
        let url = `/api/services?client=${encodeURIComponent(name)}`;
        if(month) url += `&month=${month}`;
        const r=await fetch(url),d=await r.json();
        allServices=d;renderServicesTable(d);selectedRouteId=null;currentMapFilter='all';updateFilterButtons();renderMexicoMap(document.getElementById('mexicoMap'),d);resetMapZoom();
    }catch(e){console.error(e);}
}

function renderServicesTable(services){
    const tbody=document.getElementById('servicesBody');tbody.innerHTML='';
    if(!services.length){tbody.innerHTML='<tr><td colspan="10" style="text-align:center;padding:40px;color:#64748b;">Sin servicios registrados</td></tr>';return;}
    services.forEach(s=>{
        const sc=s.arrival_time?'completed':'active',st=s.arrival_time?s.financial_status:'🔵 En Ruta';
        const cost=s.total_cost!=null?`$${s.total_cost.toFixed(2)}`:'—';
        let mins='—';
        if(s.billed_minutes!=null) {
            const h=Math.floor(s.billed_minutes/60), m=Math.floor(s.billed_minutes%60);
            mins = h>0 ? `${h}h ${m}m` : `${m}m`;
        }
        const statusOpts = ['En proceso de facturación', 'Facturado', 'Facturado y pagado', 'Pagado', 'Pendiente'];
        let statusSelect = `<select onchange="updateServiceStatus('${s.id}', this.value, this)" style="padding:4px; border-radius:4px; font-size:12px; background:var(--bg-card); color:var(--text-primary); border:1px solid var(--border-color);">`;
        statusOpts.forEach(opt => {
            statusSelect += `<option value="${opt}" ${s.financial_status === opt ? 'selected' : ''}>${opt}</option>`;
        });
        statusSelect += `</select>`;

        const tr=document.createElement('tr');
        tr.dataset.status = (s.financial_status || '').trim(); // for filtering
        tr.innerHTML=`<td>${s.unit}</td><td>${s.operator}</td><td>${s.origin}</td><td>${s.destination}</td>
        <td>
            ${s.start_time}
            <button onclick="openQuickTimeModal('${s.id}', 'start')" title="Registrar Salida" style="background:none;border:none;cursor:pointer;font-size:12px;">🕒</button>
        </td>
        <td>
            ${s.arrival_time||'<span class="status-badge active">En Ruta</span>'}
            ${!s.arrival_time ? `<button onclick="openQuickTimeModal('${s.id}', 'arrive')" title="Registrar Llegada" style="background:none;border:none;cursor:pointer;font-size:12px;">🏁</button>` : ''}
        </td>
        <td>${mins}</td><td>${cost}</td><td>${statusSelect}</td><td><div class="row-actions"><button onclick="editService('${s.id}')" title="Editar">✏️</button><button onclick="openSaveDialog('ticket','${s.id}','${s.unit}')" title="Ticket" ${!s.arrival_time?'disabled style="opacity:0.3"':''}>📄</button><button class="delete" onclick="deleteService('${s.id}')" title="Eliminar">🗑️</button></div></td>`;
        tbody.appendChild(tr);
    });
}

// ═══════ MAP FILTERS ═══════
function filterMapRoutes(filter){
    currentMapFilter=filter;
    selectedRouteId=null;
    updateFilterButtons();
    applyMapVisibility();
}

function updateFilterButtons(){
    document.querySelectorAll('.map-filter-btn').forEach(btn=>{
        btn.classList.toggle('active',btn.dataset.filter===currentMapFilter);
    });
}

function applyMapVisibility(){
    const svg=document.getElementById('mexicoMap');
    const dateFilter=document.getElementById('mapDateFilter').value; // format YYYY-MM-DD
    
    svg.querySelectorAll('.route-group').forEach(g=>{
        const isActive=g.dataset.active==='true';
        const sid=g.dataset.sid;
        const startStr=g.dataset.start;
        let visible=true;
        
        // Filter by type
        if(currentMapFilter==='active'&&!isActive) visible=false;
        if(currentMapFilter==='completed'&&isActive) visible=false;
        // Filter by selection
        if(selectedRouteId&&sid!==selectedRouteId) visible=false;
        // Filter by date
        if(dateFilter && startStr) {
            // startStr is DD/MM/YYYY hh:mm AM/PM
            const parts = startStr.split(' ')[0].split('/'); // [DD, MM, YYYY]
            if(parts.length === 3) {
                const routeDate = `${parts[2]}-${parts[1]}-${parts[0]}`; // YYYY-MM-DD
                if(routeDate !== dateFilter) visible=false;
            }
        }
        
        g.style.display = visible ? '' : 'none';
        g.style.pointerEvents = visible ? 'auto' : 'none';
    });
}

// ═══════ MAP ZOOM ═══════
function zoomMap(factor){
    mapZoomLevel=Math.max(0.5,Math.min(5,mapZoomLevel*factor));
    applyMapTransform();
}

function resetMapZoom(){
    mapZoomLevel=1;mapPanX=0;mapPanY=0;
    applyMapTransform();
}

function applyMapTransform(){
    const svg=document.getElementById('mexicoMap');
    svg.style.transform=`scale(${mapZoomLevel}) translate(${mapPanX}px,${mapPanY}px)`;
    svg.style.transformOrigin='center center';
    svg.style.transition='transform 0.3s ease';
}

// Enable drag-to-pan on map
(function(){
    let dragging=false,startX=0,startY=0;
    document.addEventListener('mousedown',e=>{
        if(e.target.closest('#mapContainer')){dragging=true;startX=e.clientX-mapPanX;startY=e.clientY-mapPanY;e.preventDefault();}
    });
    document.addEventListener('mousemove',e=>{
        if(!dragging)return;
        mapPanX=(e.clientX-startX)/mapZoomLevel;
        mapPanY=(e.clientY-startY)/mapZoomLevel;
        const svg=document.getElementById('mexicoMap');
        if(svg){svg.style.transform=`scale(${mapZoomLevel}) translate(${mapPanX}px,${mapPanY}px)`;svg.style.transition='none';}
    });
    document.addEventListener('mouseup',()=>{dragging=false;});
})();

// ═══════ MAP ROUTE CLICK ISOLATION ═══════
function onRouteClick(sid){
    if(selectedRouteId===sid){selectedRouteId=null;}
    else{selectedRouteId=sid;}
    applyMapVisibility();
}

function onMapBackgroundClick(e){
    // Only if clicking on a state (background), not a route
    if(e.target.classList.contains('mexico-state')){
        selectedRouteId=null;
        applyMapVisibility();
    }
}

function filterTable(){
    const q=document.getElementById('searchInput').value.toLowerCase();
    const currentStatus = document.querySelector('.status-filters .active')?.dataset.status || 'all';
    document.querySelectorAll('#servicesBody tr').forEach(r=>{
        const matchesQuery = r.textContent.toLowerCase().includes(q);
        const rowStatus = (r.dataset.status || '').trim();
        const matchesStatus = currentStatus === 'all' || rowStatus === currentStatus;
        r.style.display = (matchesQuery && matchesStatus) ? '' : 'none';
    });
}

function filterTableByStatus(status) {
    document.querySelectorAll('.status-filters button').forEach(b => b.classList.remove('active'));
    document.querySelector(`.status-filters button[data-status="${status}"]`)?.classList.add('active');
    filterTable();
}

function openModal(editData=null){
    document.getElementById('serviceModal').classList.add('show');
    document.getElementById('modalTitle').textContent=editData?'Editar Servicio':'Nuevo Servicio';
    document.getElementById('serviceForm').reset();document.getElementById('editingId').value='';
    if(currentClient)document.getElementById('fClient').value=currentClient;
    const now=new Date();document.getElementById('fStartDate').value=now.toLocaleDateString('es-MX',{day:'2-digit',month:'2-digit',year:'numeric'});
    if(editData){
        document.getElementById('editingId').value=editData.id;
        document.getElementById('fUnit').value=editData.unit;document.getElementById('fOperator').value=editData.operator;
        document.getElementById('fClient').value=editData.client;document.getElementById('fOrigin').value=editData.origin;
        document.getElementById('fDestination').value=editData.destination;document.getElementById('fRate').value=editData.hourly_rate;
        document.getElementById('fStatus').value=editData.financial_status;
        if(editData.start_time){const p=parseTimeString(editData.start_time);if(p){document.getElementById('fStartDate').value=p.date;document.getElementById('fStartHour').value=p.hour;document.getElementById('fStartMinute').value=p.minute;document.getElementById('fStartAmpm').value=p.ampm;}}
        if(editData.arrival_time){const p=parseTimeString(editData.arrival_time);if(p){document.getElementById('fEndDate').value=p.date;document.getElementById('fEndHour').value=p.hour;document.getElementById('fEndMinute').value=p.minute;document.getElementById('fEndAmpm').value=p.ampm;}}
    }
}
function parseTimeString(str){const m=str.match(/(\d{2}\/\d{2}\/\d{4})\s+(\d{1,2}):(\d{2})\s+(AM|PM)/i);return m?{date:m[1],hour:m[2],minute:m[3],ampm:m[4].toUpperCase()}:null;}
function closeModal(){document.getElementById('serviceModal').classList.remove('show');}

async function saveService(){
    const editId=document.getElementById('editingId').value;
    const unit=document.getElementById('fUnit').value.trim(),operator=document.getElementById('fOperator').value.trim(),client=document.getElementById('fClient').value.trim(),origin=document.getElementById('fOrigin').value.trim(),destination=document.getElementById('fDestination').value.trim(),rate=document.getElementById('fRate').value.trim(),status=document.getElementById('fStatus').value;
    if(!unit||!operator||!client||!origin||!destination||!rate){showToast('Completa todos los campos obligatorios','error');return;}
    const startTime=`${document.getElementById('fStartDate').value} ${document.getElementById('fStartHour').value}:${document.getElementById('fStartMinute').value} ${document.getElementById('fStartAmpm').value}`;
    let arrivalTime='';const ed=document.getElementById('fEndDate').value,eh=document.getElementById('fEndHour').value,em=document.getElementById('fEndMinute').value;
    if(ed&&eh&&em)arrivalTime=`${ed} ${eh}:${em} ${document.getElementById('fEndAmpm').value}`;
    const body={unit,operator,client,origin,destination,hourly_rate:parseFloat(rate),start_time:startTime,arrival_time:arrivalTime||null,financial_status:status};
    try{
        const res=editId?await fetch(`/api/services/${editId}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}):await fetch('/api/services',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
        const data=await res.json();
        if(res.ok){showToast(editId?'Servicio actualizado':'Servicio registrado');closeModal();loadClients();if(currentClient){loadClientStats(currentClient);loadClientServices(currentClient);}}
        else showToast(data.error||'Error al guardar','error');
    }catch(e){showToast('Error de conexión','error');}
}

async function editService(id){try{const r=await fetch(`/api/services?client=${encodeURIComponent(currentClient)}`),s=await r.json(),f=s.find(x=>x.id===id);if(f)openModal(f);}catch(e){showToast('Error cargando servicio','error');}}
async function deleteService(id){if(!confirm('¿Eliminar este servicio?'))return;try{await fetch(`/api/services/${id}`,{method:'DELETE'});showToast('Servicio eliminado');loadClients();if(currentClient){loadClientStats(currentClient);loadClientServices(currentClient);}}catch(e){showToast('Error al eliminar','error');}}

// ═══════ NATIVE OS SAVE FILE DIALOG ═══════
async function openSaveDialog(type, serviceId='', unitName=''){
    try {
        let defaultName = '';
        let acceptOpts = {};
        
        if (type === 'csv') {
            defaultName = `Reporte_${(currentClient||'').replace(/\s+/g,'_')}.csv`;
            acceptOpts = { 'text/csv': ['.csv'] };
        } else if (type === 'ticket') {
            defaultName = `Ticket_${unitName.replace(/\s+/g,'_')}.pdf`;
            acceptOpts = { 'application/pdf': ['.pdf'] };
        }

        // Trigger native OS Save As dialog
        const handle = await window.showSaveFilePicker({
            suggestedName: defaultName,
            types: [{
                description: type === 'csv' ? 'Archivo CSV' : 'Ticket PDF',
                accept: acceptOpts
            }]
        });

        // Fetch the generated file content from the backend
        let response;
        if (type === 'csv') {
            response = await fetch(`/api/export_csv?client=${encodeURIComponent(currentClient)}`);
        } else if (type === 'ticket') {
            response = await fetch(`/api/ticket/${serviceId}`);
        }

        if (!response || !response.ok) {
            showToast('Error generando archivo', 'error');
            return;
        }

        const blob = await response.blob();
        
        // Write directly to the path chosen by the user in the native dialog
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        
        showToast('Archivo guardado exitosamente');

    } catch (err) {
        if (err.name !== 'AbortError') {
            // Only show error if it's not a user cancellation
            showToast('Error al guardar', 'error');
            console.error(err);
        }
    }
}

// CSV Export
function exportCSV(){
    if(!currentClient){showToast('Selecciona un cliente primero','error');return;}
    openSaveDialog('csv');
}

// ═══════ FACTURA GLOBAL ═══════
function openInvoiceModal(){
    if(!currentClient){showToast('Selecciona un cliente primero','error');return;}
    document.getElementById('invoiceModal').classList.add('show');
    document.getElementById('invStartDate').value='';
    document.getElementById('invEndDate').value='';
    document.getElementById('invIva').value='16';
}

function closeInvoiceModal(){
    document.getElementById('invoiceModal').classList.remove('show');
}

async function generateInvoice(){
    const sd=document.getElementById('invStartDate').value;
    const ed=document.getElementById('invEndDate').value;
    const iva=document.getElementById('invIva').value;
    
    closeInvoiceModal();
    
    try {
        const defaultName = `Factura_${currentClient.replace(/\s+/g,'_')}.pdf`;
        const handle = await window.showSaveFilePicker({
            suggestedName: defaultName,
            types: [{ description: 'Factura PDF', accept: { 'application/pdf': ['.pdf'] } }]
        });

        const body = { client: currentClient, start_date: sd, end_date: ed, iva: iva };
        const response = await fetch('/api/invoice_blob', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const data = await response.json().catch(()=>({}));
            showToast(data.error || 'Error generando factura', 'error');
            return;
        }

        const blob = await response.blob();
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        
        showToast('Factura guardada exitosamente');
    } catch (err) {
        if (err.name !== 'AbortError') {
            showToast('Error al guardar', 'error');
            console.error(err);
        }
    }
}
// ═══════ NUEVAS FUNCIONES ═══════
function applyGlobalMonthFilter() {
    loadClients();
    if(currentClient) {
        loadClientStats(currentClient);
        loadClientServices(currentClient);
    }
}

function toggleClientActions() {
    const menu = document.getElementById('clientActionsMenu');
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

document.addEventListener('click', e => {
    const dropdown = document.getElementById('clientActionsDropdown');
    const menu = document.getElementById('clientActionsMenu');
    if (dropdown && menu && !dropdown.contains(e.target)) {
        menu.style.display = 'none';
    }
});

async function inactivateClient() {
    if(!confirm('¿Estás seguro de que deseas inactivar este cliente? Sus datos no se mostrarán en los reportes globales.')) return;
    try {
        await fetch(`/api/clients/${encodeURIComponent(currentClient)}/status`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'inactivate'})
        });
        showToast('Cliente inactivado');
        clearClientSelection();
        loadClients();
    } catch(e) {
        showToast('Error al inactivar cliente', 'error');
    }
}

async function deleteClient() {
    if(!confirm('¿Estás seguro de que deseas ELIMINAR este cliente y todos sus servicios? Esta acción no se puede deshacer.')) return;
    try {
        await fetch(`/api/clients/${encodeURIComponent(currentClient)}/status`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'delete'})
        });
        showToast('Cliente eliminado');
        clearClientSelection();
        loadClients();
    } catch(e) {
        showToast('Error al eliminar cliente', 'error');
    }
}

let currentQuickAction = null;
let currentQuickServiceId = null;

function openQuickTimeModal(serviceId, actionStr) {
    currentQuickServiceId = serviceId;
    currentQuickAction = actionStr;
    const isStart = actionStr === 'start';
    document.getElementById('quickTimeTitle').textContent = isStart ? 'Registrar Salida' : 'Registrar Llegada';
    
    // Set to current time
    const now = new Date();
    document.getElementById('qtDate').value = now.toLocaleDateString('es-MX', {day:'2-digit',month:'2-digit',year:'numeric'});
    let h = now.getHours();
    const m = Math.floor(now.getMinutes()/5)*5;
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    h = h ? h : 12;
    document.getElementById('qtHour').value = h.toString().padStart(2, '0');
    document.getElementById('qtMinute').value = m.toString().padStart(2, '0');
    document.getElementById('qtAmpm').value = ampm;
    
    document.getElementById('quickTimeModal').classList.add('show');
}

function closeQuickTimeModal() {
    document.getElementById('quickTimeModal').classList.remove('show');
}

async function saveQuickTime() {
    const d = document.getElementById('qtDate').value;
    const h = document.getElementById('qtHour').value;
    const m = document.getElementById('qtMinute').value;
    const ampm = document.getElementById('qtAmpm').value;
    if(!d || !h || !m) { showToast('Completa la fecha y hora', 'error'); return; }
    
    const valueStr = `${d} ${h}:${m} ${ampm}`;
    try {
        const res = await fetch(`/api/services/${currentQuickServiceId}/quick_action`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: currentQuickAction, value: valueStr})
        });
        if(res.ok) {
            showToast('Actualizado');
            closeQuickTimeModal();
            if(currentClient) {
                loadClientStats(currentClient);
                loadClientServices(currentClient);
            }
        } else {
            showToast('Error', 'error');
        }
    } catch(e) {
        showToast('Error de red', 'error');
    }
}

async function updateServiceStatus(serviceId, status, selectEl) {
    try {
        const res = await fetch(`/api/services/${serviceId}/quick_action`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'status', value: status})
        });
        if(res.ok) {
            showToast('Estado actualizado');
            if(selectEl) {
                const tr = selectEl.closest('tr');
                if(tr) {
                    tr.dataset.status = status;
                    filterTable();
                }
            }
        } else {
            showToast('Error', 'error');
        }
    } catch(e) {
        showToast('Error de red', 'error');
    }
}
