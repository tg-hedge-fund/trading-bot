--
-- PostgreSQL database dump
--

\restrict EF2WZa9forntEFaN1wdFhXCgmDWFteO0FT16cGInXtHhHcJcH9EzFPGhFnLO2ff

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
-- Name: instrument_idx; Type: TABLE; Schema: primary; Owner: postgres
--

CREATE TABLE IF NOT EXISTS "primary".instrument_idx (
    exchange_token character varying(255) NOT NULL,
    trading_symbol character varying(255) NOT NULL,
    exchange character varying(255) NOT NULL,
    groww_symbol character varying(255) NOT NULL,
    name character varying(255),
    instrument_type character varying(255) NOT NULL,
    segment character varying(255) NOT NULL,
    series character varying(255),
    isin character varying(255) NOT NULL,
    underlying_symbol character varying(255),
    underlying_exchange_token bigint,
    expiry_date timestamp(6) without time zone,
    strike_price double precision,
    lot_size bigint,
    tick_size double precision,
    freeze_quantity bigint,
    is_reserved integer,
    buy_allowed integer,
    sell_allowed integer,
    internal_trading_symbol character varying(255),
    is_intraday integer,
    creation_ts timestamp with time zone DEFAULT (now() AT TIME ZONE 'UTC'::text)
);


ALTER TABLE "primary".instrument_idx OWNER TO tghfadm;

--
-- Name: instrument_idx instrument_idx_pkey; Type: CONSTRAINT; Schema: primary; Owner: postgres
--

ALTER TABLE ONLY "primary".instrument_idx
    ADD CONSTRAINT instrument_idx_pkey PRIMARY KEY (exchange_token, trading_symbol);


--
-- PostgreSQL database dump complete
--

\unrestrict EF2WZa9forntEFaN1wdFhXCgmDWFteO0FT16cGInXtHhHcJcH9EzFPGhFnLO2ff
