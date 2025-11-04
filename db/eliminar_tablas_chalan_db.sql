-- Script SQL para eliminar todas las tablas de chalan-db en Render
-- Ejecutar desde el Web Shell de Render: python manage.py dbshell
-- Copia y pega todo este bloque en el dbshell

-- Eliminar tablas de appschedule
DROP TABLE IF EXISTS appschedule_event CASCADE;
DROP TABLE IF EXISTS appschedule_eventdraft CASCADE;
DROP TABLE IF EXISTS appschedule_eventimage CASCADE;
DROP TABLE IF EXISTS appschedule_eventnote CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatmessage CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatreadstatus CASCADE;
DROP TABLE IF EXISTS appschedule_absencereason CASCADE;

-- Eliminar tablas de apptransactions
DROP TABLE IF EXISTS apptransactions_documentline CASCADE;
DROP TABLE IF EXISTS apptransactions_document CASCADE;
DROP TABLE IF EXISTS apptransactions_documenttype CASCADE;
DROP TABLE IF EXISTS apptransactions_partytype CASCADE;
DROP TABLE IF EXISTS apptransactions_partycategory CASCADE;
DROP TABLE IF EXISTS apptransactions_party CASCADE;
DROP TABLE IF EXISTS apptransactions_workaccount CASCADE;
DROP TABLE IF EXISTS apptransactions_transactionfavorite CASCADE;

-- Eliminar tablas de auditapp
DROP TABLE IF EXISTS auditapp_useractionlog CASCADE;

-- Eliminar tablas de crewsapp
DROP TABLE IF EXISTS crewsapp_category CASCADE;
DROP TABLE IF EXISTS crewsapp_crew CASCADE;
DROP TABLE IF EXISTS crewsapp_truck CASCADE;
DROP TABLE IF EXISTS crewsapp_truckassignment CASCADE;

-- Eliminar tablas de ctrctsapp
DROP TABLE IF EXISTS ctrctsapp_contractdetails CASCADE;
DROP TABLE IF EXISTS ctrctsapp_contract CASCADE;
DROP TABLE IF EXISTS ctrctsapp_workprice CASCADE;
DROP TABLE IF EXISTS ctrctsapp_housemodel CASCADE;
DROP TABLE IF EXISTS ctrctsapp_job CASCADE;
DROP TABLE IF EXISTS ctrctsapp_builder CASCADE;

-- Eliminar registros de migraciones de estas apps
DELETE FROM django_migrations WHERE app IN ('appschedule', 'apptransactions', 'auditapp', 'crewsapp', 'ctrctsapp');
