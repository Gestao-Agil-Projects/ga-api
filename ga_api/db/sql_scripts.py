class SqlScripts:

    @staticmethod
    def create_root_admin() -> str:
        return """
                INSERT INTO users (
            id,
            email,
            hashed_password,
            is_active,
            is_superuser,
            is_verified,
            full_name,
            image_url,
            bio,
            cpf,
            phone,
            birth_date,
            frequency,
            role,
            created_at,
            updated_at
        ) VALUES (
            gen_random_uuid(),
            'admin@admin.com',
            '$argon2id$v=19$m=65536,t=3,p=4$phgnTWqeFggJ8YBnAAeBdQ$MRg/9B/dnAhstohoTuCQdzofwHWAihUrOFB6Pk3e7G4',
            true,
            true,
            true,
            'Admin',
            NULL,
            NULL,
            '000.000.000-00',
            NULL,
            NULL,
            'WEEKLY',
            'PATIENT',
            now(),
            now()
        ) ON CONFLICT DO NOTHING;
        """
