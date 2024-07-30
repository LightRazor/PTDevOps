DROP TABLE IF EXISTS public.emails;
CREATE TABLE IF NOT EXISTS public.emails
(
    id uuid DEFAULT gen_random_uuid(),
    email text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT emails_pkey PRIMARY KEY (email)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.emails
    OWNER to postgres;

DROP TABLE IF EXISTS public.phones;
CREATE TABLE IF NOT EXISTS public.phones
(
    id uuid DEFAULT gen_random_uuid(),
    phone text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT phones_pkey PRIMARY KEY (phone)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.phones
    OWNER to postgres;