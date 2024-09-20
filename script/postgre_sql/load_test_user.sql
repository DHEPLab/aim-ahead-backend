DO $$
DECLARE
    i INT := 1;          
    user_count INT := 10;
BEGIN
    WHILE i <= user_count LOOP
        INSERT INTO public.user (name, email, password, salt, active) 
            VALUES ('Test User', CONCAT('user', i, '@test.com'), ?, ?, true);
        i := i + 1;
    END LOOP;
END $$;
