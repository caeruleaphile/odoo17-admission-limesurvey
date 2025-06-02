def migrate(cr, version):
    # Ajout de la colonne state si elle n'existe pas
    cr.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'admission_survey_template' 
                AND column_name = 'state'
            ) THEN
                ALTER TABLE admission_survey_template 
                ADD COLUMN state varchar DEFAULT 'draft' NOT NULL;
            END IF;
        END
        $$;
    """) 