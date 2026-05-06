import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.connection import engine, Base
from database.models import MonitoringService

def init_db():
    print("Iniciando conexión con Supabase...")
    with engine.connect() as conn:
        print("Creando tipo ENUM financial_status_enum (si no existe)...")
        try:
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE financial_status_enum AS ENUM (
                        'Facturado y pagado',
                        'Pagado',
                        'En proceso de facturación'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            print("ENUM listo.")
        except Exception as e:
            print(f"Nota sobre ENUM: {e}")

        print("Creando tablas con SQLAlchemy...")
        # Esto creará la tabla monitoring_services si no existe
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas.")

        print("Instalando Función de Cálculo de Tiempo/Dinero...")
        try:
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION calculate_service_cost()
                RETURNS TRIGGER AS $$
                DECLARE
                    raw_minutes NUMERIC;
                    rounded_minutes INTEGER;
                    cost_per_minute NUMERIC;
                BEGIN
                    IF NEW.start_time IS NOT NULL AND NEW.arrival_time IS NOT NULL THEN
                        -- Diferencia en minutos
                        raw_minutes := EXTRACT(EPOCH FROM (NEW.arrival_time - NEW.start_time)) / 60;
                        
                        -- Redondeo hacia arriba a múltiplo de 5 (ej: 42 -> 45)
                        rounded_minutes := CEIL(raw_minutes / 5.0) * 5;
                        
                        -- Cálculo de dinero
                        cost_per_minute := NEW.hourly_rate / 60.0;
                        
                        NEW.billed_minutes := rounded_minutes;
                        NEW.total_cost := ROUND((cost_per_minute * rounded_minutes)::NUMERIC, 2);
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            print("Función instalada.")
        except Exception as e:
            print(f"Error creando función: {e}")

        print("Instalando Trigger...")
        try:
            conn.execute(text("""
                DROP TRIGGER IF EXISTS trigger_calculate_service_cost ON monitoring_services;
                CREATE TRIGGER trigger_calculate_service_cost
                BEFORE INSERT OR UPDATE ON monitoring_services
                FOR EACH ROW
                EXECUTE FUNCTION calculate_service_cost();
            """))
            print("Trigger instalado.")
        except Exception as e:
            print(f"Error creando trigger: {e}")

        conn.commit()
        print("¡Base de datos preparada con éxito!")

if __name__ == '__main__':
    init_db()
