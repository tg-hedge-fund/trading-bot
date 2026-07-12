CREATE TABLE IF NOT EXISTS "primary".watchlist (
    exchange_token character varying(255) CONSTRAINT instruments_exchange_token_not_null NOT NULL,
    trading_symbol character varying(255) CONSTRAINT instruments_trading_symbol_not_null NOT NULL,
    exchange character varying(255) CONSTRAINT instruments_exchange_not_null NOT NULL,
    groww_symbol character varying(255) CONSTRAINT instruments_groww_symbol_not_null NOT NULL,
    name character varying(255),
    instrument_type character varying(255) CONSTRAINT instruments_instrument_type_not_null NOT NULL,
    segment character varying(255) CONSTRAINT instruments_segment_not_null NOT NULL,
    series character varying(255),
    isin character varying(255) CONSTRAINT instruments_isin_not_null NOT NULL
);

ALTER TABLE "primary".watchlist OWNER TO tghfadm;

ALTER TABLE ONLY "primary".watchlist
    ADD CONSTRAINT watchlist_pkey PRIMARY KEY (exchange_token, trading_symbol);

ALTER TABLE "primary".watchlist
    ADD COLUMN creation_ts timestamp with time zone DEFAULT now();
