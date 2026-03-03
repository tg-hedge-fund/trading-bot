--
-- PostgreSQL database dump
--

\restrict HwAYaZaTSWMt93c10KWerz39pD3ZphppnRQo2tR7ObOKPPHJ76o3Ojq4A7tdHeV

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.1 (Debian 18.1-1.pgdg13+2)

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
-- Name: portfolio; Type: TABLE; Schema: primary; Owner: postgres
--

CREATE TABLE "primary".portfolio (
    isin character varying(255) NOT NULL,
    active_demat_transfer_quantity integer,
    average_price double precision,
    corporate_action_additional_quantity integer,
    demat_free_quantity double precision,
    demat_locked_quantity double precision,
    groww_locked_quantity double precision,
    pledge_quantity double precision,
    quantity double precision,
    repledge_quantity double precision,
    t1_quantity double precision,
    tradable_exchanges character varying(255),
    trading_symbol character varying(255),
    creation_ts timestamp with time zone DEFAULT (now() AT TIME ZONE 'UTC'::text)
);


ALTER TABLE "primary".portfolio OWNER TO postgres;

--
-- Name: portfolio portfolio_pkey; Type: CONSTRAINT; Schema: primary; Owner: postgres
--

ALTER TABLE ONLY "primary".portfolio
    ADD CONSTRAINT portfolio_pkey PRIMARY KEY (isin);


--
-- PostgreSQL database dump complete
--

\unrestrict HwAYaZaTSWMt93c10KWerz39pD3ZphppnRQo2tR7ObOKPPHJ76o3Ojq4A7tdHeV

