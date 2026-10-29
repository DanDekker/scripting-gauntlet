--
-- PostgreSQL database dump
--

SET statement_timeout = 0;

COPY public.orders (id, customer, region, amount) FROM stdin;
1	ACME	North	1250.00
2	GLOBEX	South	980.50
3	ACME	North	310.25
4	INITECH	East	610.00
\.

COPY public.customers (id, name) FROM stdin;
1	ACME Corp
2	GLOBEX Ltd
\.
