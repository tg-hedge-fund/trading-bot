--
-- PostgreSQL database dump
--

\restrict gE6hkyiwj3CCFIndQV4zgaajxZWp3U6QngtmA9vNsX6vwhtZ0gTXK41YwUm7JO8

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
-- Name: instrument_eq; Type: TABLE; Schema: primary; Owner: postgres
--

CREATE TABLE IF NOT EXISTS "primary".instrument_eq (
    exchange_token character varying(255) CONSTRAINT instruments_exchange_token_not_null NOT NULL,
    trading_symbol character varying(255) CONSTRAINT instruments_trading_symbol_not_null NOT NULL,
    exchange character varying(255) CONSTRAINT instruments_exchange_not_null NOT NULL,
    groww_symbol character varying(255) CONSTRAINT instruments_groww_symbol_not_null NOT NULL,
    name character varying(255),
    instrument_type character varying(255) CONSTRAINT instruments_instrument_type_not_null NOT NULL,
    segment character varying(255) CONSTRAINT instruments_segment_not_null NOT NULL,
    series character varying(255),
    isin character varying(255) CONSTRAINT instruments_isin_not_null NOT NULL,
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
    market_cap double precision,
    creation_ts timestamp with time zone DEFAULT (now() AT TIME ZONE 'UTC'::text)
);


ALTER TABLE "primary".instrument_eq OWNER TO tghfadm;

--
-- Name: instrument_eq instruments_pkey; Type: CONSTRAINT; Schema: primary; Owner: postgres
--

ALTER TABLE ONLY "primary".instrument_eq
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (exchange_token, trading_symbol);


--
-- PostgreSQL database dump complete
--

\unrestrict gE6hkyiwj3CCFIndQV4zgaajxZWp3U6QngtmA9vNsX6vwhtZ0gTXK41YwUm7JO8
