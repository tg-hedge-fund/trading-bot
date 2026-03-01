--
-- PostgreSQL database dump
--

\restrict h80eB6yZljMnv7AZMjdGV02AOT03eoomXF4oeakPbLzVJf7gKY1ggHxlCkAouB3

-- Dumped from database version 18.2 (Debian 18.2-1.pgdg13+1)
-- Dumped by pg_dump version 18.2 (Debian 18.2-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: primary; Owner: tghfadm
--

CREATE TABLE "primary".users (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE "primary".users OWNER TO tghfadm;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: primary; Owner: tghfadm
--

CREATE SEQUENCE "primary".users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "primary".users_id_seq OWNER TO tghfadm;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: primary; Owner: tghfadm
--

ALTER SEQUENCE "primary".users_id_seq OWNED BY "primary".users.id;


--
-- Name: users id; Type: DEFAULT; Schema: primary; Owner: tghfadm
--

ALTER TABLE ONLY "primary".users ALTER COLUMN id SET DEFAULT nextval('"primary".users_id_seq'::regclass);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: primary; Owner: tghfadm
--

ALTER TABLE ONLY "primary".users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: primary; Owner: tghfadm
--

ALTER TABLE ONLY "primary".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict h80eB6yZljMnv7AZMjdGV02AOT03eoomXF4oeakPbLzVJf7gKY1ggHxlCkAouB3

