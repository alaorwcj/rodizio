--
-- PostgreSQL database dump
--

\restrict pgdqByVdAuMeNuxIqey3MaNSPFef5JPdUBR0b7FdCFl0rc4WgccteLaF0CzIaDI

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: comum_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comum_config (
    comum_id character varying(50) NOT NULL,
    periodo_inicio date,
    periodo_fim date,
    fechamento_publicacao_dias integer,
    dias_culto jsonb,
    horarios jsonb,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.comum_config OWNER TO postgres;

--
-- Name: comum_horarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comum_horarios (
    id integer NOT NULL,
    comum_id character varying(50) NOT NULL,
    dia_semana character varying(20) NOT NULL,
    meia_hora time without time zone,
    culto time without time zone,
    rjm time without time zone
);


ALTER TABLE public.comum_horarios OWNER TO postgres;

--
-- Name: comum_horarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comum_horarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comum_horarios_id_seq OWNER TO postgres;

--
-- Name: comum_horarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comum_horarios_id_seq OWNED BY public.comum_horarios.id;


--
-- Name: comuns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comuns (
    id character varying(50) NOT NULL,
    sub_regional_id character varying(50) NOT NULL,
    nome character varying(200) NOT NULL,
    endereco text,
    cidade character varying(100),
    ativo boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.comuns OWNER TO postgres;

--
-- Name: TABLE comuns; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.comuns IS 'Comuns (igrejas) dentro de cada sub-regional';


--
-- Name: escala; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.escala (
    id integer NOT NULL,
    comum_id character varying(50) NOT NULL,
    data date NOT NULL,
    dia_semana character varying(20),
    meia_hora character varying(200),
    culto character varying(200),
    criado_em timestamp with time zone DEFAULT now(),
    criado_por character varying(50)
);


ALTER TABLE public.escala OWNER TO postgres;

--
-- Name: TABLE escala; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.escala IS 'Escala de cultos regulares e meia-hora';


--
-- Name: escala_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.escala_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.escala_id_seq OWNER TO postgres;

--
-- Name: escala_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.escala_id_seq OWNED BY public.escala.id;


--
-- Name: escala_publicacao; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.escala_publicacao (
    comum_id character varying(50) NOT NULL,
    publicada_em timestamp with time zone,
    publicada_por character varying(50),
    periodo_inicio date,
    periodo_fim date
);


ALTER TABLE public.escala_publicacao OWNER TO postgres;

--
-- Name: escala_rjm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.escala_rjm (
    id character varying(100) NOT NULL,
    comum_id character varying(50) NOT NULL,
    data date NOT NULL,
    dia_semana character varying(20),
    organista character varying(200),
    criado_em timestamp with time zone DEFAULT now(),
    criado_por character varying(50)
);


ALTER TABLE public.escala_rjm OWNER TO postgres;

--
-- Name: TABLE escala_rjm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.escala_rjm IS 'Escala específica para RJM (Reunião de Jovens e Menores)';


--
-- Name: indisponibilidades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.indisponibilidades (
    id integer NOT NULL,
    comum_id character varying(50) NOT NULL,
    organista_id character varying(50) NOT NULL,
    data date NOT NULL,
    motivo text,
    autor character varying(50),
    status character varying(20),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.indisponibilidades OWNER TO postgres;

--
-- Name: TABLE indisponibilidades; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.indisponibilidades IS 'Datas em que organistas estão indisponíveis';


--
-- Name: indisponibilidades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.indisponibilidades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.indisponibilidades_id_seq OWNER TO postgres;

--
-- Name: indisponibilidades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.indisponibilidades_id_seq OWNED BY public.indisponibilidades.id;


--
-- Name: logs_auditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.logs_auditoria (
    id character varying(100) NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    tipo character varying(50),
    categoria character varying(50),
    acao character varying(100),
    descricao text,
    usuario_id character varying(50),
    usuario_nome character varying(200),
    usuario_tipo character varying(50),
    regional_id character varying(50),
    sub_regional_id character varying(50),
    comum_id character varying(50),
    status character varying(20),
    ip character varying(45),
    user_agent text,
    dados_antes jsonb,
    dados_depois jsonb
);


ALTER TABLE public.logs_auditoria OWNER TO postgres;

--
-- Name: TABLE logs_auditoria; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.logs_auditoria IS 'Logs de auditoria de todas as operações';


--
-- Name: organista_dias_permitidos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organista_dias_permitidos (
    organista_id character varying(50) NOT NULL,
    dia character varying(20) NOT NULL
);


ALTER TABLE public.organista_dias_permitidos OWNER TO postgres;

--
-- Name: TABLE organista_dias_permitidos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organista_dias_permitidos IS 'Dias da semana em que cada organista está disponível';


--
-- Name: organista_regras_especiais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organista_regras_especiais (
    organista_id character varying(50) NOT NULL,
    chave character varying(100) NOT NULL,
    valor text
);


ALTER TABLE public.organista_regras_especiais OWNER TO postgres;

--
-- Name: organista_tipos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organista_tipos (
    organista_id character varying(50) NOT NULL,
    tipo character varying(50) NOT NULL
);


ALTER TABLE public.organista_tipos OWNER TO postgres;

--
-- Name: TABLE organista_tipos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organista_tipos IS 'Tipos de culto que cada organista pode tocar (Meia-hora, Culto, RJM)';


--
-- Name: organistas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organistas (
    id character varying(50) NOT NULL,
    comum_id character varying(50) NOT NULL,
    nome character varying(200) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.organistas OWNER TO postgres;

--
-- Name: TABLE organistas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organistas IS 'Organistas cadastrados em cada comum';


--
-- Name: regionais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regionais (
    id character varying(50) NOT NULL,
    nome character varying(200) NOT NULL,
    ativo boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.regionais OWNER TO postgres;

--
-- Name: TABLE regionais; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.regionais IS 'Regionais da organização';


--
-- Name: sub_regionais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sub_regionais (
    id character varying(50) NOT NULL,
    regional_id character varying(50) NOT NULL,
    nome character varying(200) NOT NULL,
    ativo boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sub_regionais OWNER TO postgres;

--
-- Name: TABLE sub_regionais; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sub_regionais IS 'Sub-regionais dentro de cada regional';


--
-- Name: trocas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trocas (
    id character varying(100) NOT NULL,
    comum_id character varying(50) NOT NULL,
    status character varying(20),
    modalidade character varying(50),
    tipo character varying(50),
    data date,
    slot character varying(50),
    solicitante_id character varying(50),
    solicitante_nome character varying(200),
    alvo_id character varying(50),
    alvo_nome character varying(200),
    motivo text,
    criado_em timestamp with time zone DEFAULT now(),
    atualizado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.trocas OWNER TO postgres;

--
-- Name: TABLE trocas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.trocas IS 'Sistema de trocas de escala entre organistas';


--
-- Name: trocas_historico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trocas_historico (
    id integer NOT NULL,
    troca_id character varying(100) NOT NULL,
    quando timestamp with time zone NOT NULL,
    acao character varying(50),
    por character varying(200)
);


ALTER TABLE public.trocas_historico OWNER TO postgres;

--
-- Name: trocas_historico_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trocas_historico_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trocas_historico_id_seq OWNER TO postgres;

--
-- Name: trocas_historico_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trocas_historico_id_seq OWNED BY public.trocas_historico.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id character varying(50) NOT NULL,
    nome character varying(200) NOT NULL,
    password_hash text NOT NULL,
    tipo character varying(50) NOT NULL,
    nivel character varying(50) NOT NULL,
    contexto_id character varying(50),
    ativo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: TABLE usuarios; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.usuarios IS 'Usuários do sistema (master, admins, encarregados)';


--
-- Name: comum_horarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_horarios ALTER COLUMN id SET DEFAULT nextval('public.comum_horarios_id_seq'::regclass);


--
-- Name: escala id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala ALTER COLUMN id SET DEFAULT nextval('public.escala_id_seq'::regclass);


--
-- Name: indisponibilidades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.indisponibilidades ALTER COLUMN id SET DEFAULT nextval('public.indisponibilidades_id_seq'::regclass);


--
-- Name: trocas_historico id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trocas_historico ALTER COLUMN id SET DEFAULT nextval('public.trocas_historico_id_seq'::regclass);


--
-- Data for Name: comum_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comum_config (comum_id, periodo_inicio, periodo_fim, fechamento_publicacao_dias, dias_culto, horarios, updated_at) FROM stdin;
\.


--
-- Data for Name: comum_horarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comum_horarios (id, comum_id, dia_semana, meia_hora, culto, rjm) FROM stdin;
\.


--
-- Data for Name: comuns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comuns (id, sub_regional_id, nome, endereco, cidade, ativo, created_at, updated_at) FROM stdin;
vila_paula	santa_isabel	Comum Vila Paula		Santa Isabel	t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
central	santa_isabel	Central			t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
pedra_branca	santa_isabel	Pedra Branca			t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
jdcristina	santa_isabel	Jardim Cristina			t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
teste	santa_isabel	teste			t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
atibaia-jardim	sub-atibaia	Atibaia Jardim			t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
\.


--
-- Data for Name: escala; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.escala (id, comum_id, data, dia_semana, meia_hora, culto, criado_em, criado_por) FROM stdin;
910	vila_paula	2025-10-05	Sunday	Ieda	Ieda	2025-10-26 17:35:08.231323+00	\N
911	vila_paula	2025-10-07	Tuesday	Ieda	Ieda	2025-10-26 17:35:08.231323+00	\N
912	vila_paula	2025-10-12	Sunday	Yasmin G.	Raquel	2025-10-26 17:35:08.231323+00	\N
913	vila_paula	2025-10-14	Tuesday	Milena	Milena	2025-10-26 17:35:08.231323+00	\N
914	vila_paula	2025-10-19	Sunday	Yasmin G.	Janaina	2025-10-26 17:35:08.231323+00	\N
915	vila_paula	2025-10-21	Tuesday	Ieda	Ieda	2025-10-26 17:35:08.231323+00	\N
916	vila_paula	2025-10-26	Sunday	Yasmin C.	Raquel	2025-10-26 17:35:08.231323+00	\N
917	vila_paula	2025-10-28	Tuesday	Milena	Milena	2025-10-26 17:35:08.231323+00	\N
918	vila_paula	2025-11-02	Sunday	Yasmin C.	Ieda	2025-10-26 17:35:08.231323+00	\N
919	vila_paula	2025-11-04	Tuesday	Milena	Milena	2025-10-26 17:35:08.231323+00	\N
920	vila_paula	2025-11-09	Sunday	Yasmin G.	Raquel	2025-10-26 17:35:08.231323+00	\N
921	vila_paula	2025-11-11	Tuesday	Ieda	Ieda	2025-10-26 17:35:08.231323+00	\N
922	vila_paula	2025-11-16	Sunday	Yasmin C.	Milena	2025-10-26 17:35:08.231323+00	\N
923	vila_paula	2025-11-18	Tuesday	Milena	Milena	2025-10-26 17:35:08.231323+00	\N
924	vila_paula	2025-11-23	Sunday	Yasmin G.	Janaina	2025-10-26 17:35:08.231323+00	\N
925	vila_paula	2025-11-25	Tuesday	Ieda	Ieda	2025-10-26 17:35:08.231323+00	\N
926	vila_paula	2025-11-30	Sunday	Yasmin C.	Milena	2025-10-26 17:35:08.231323+00	\N
927	pedra_branca	2025-10-14	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
928	pedra_branca	2025-10-17	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
929	pedra_branca	2025-10-19	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
930	pedra_branca	2025-10-21	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
931	pedra_branca	2025-10-24	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
932	pedra_branca	2025-10-26	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
933	pedra_branca	2025-10-28	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
934	pedra_branca	2025-10-31	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
935	pedra_branca	2025-11-02	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
936	pedra_branca	2025-11-04	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
937	pedra_branca	2025-11-07	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
938	pedra_branca	2025-11-09	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
939	pedra_branca	2025-11-11	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
940	pedra_branca	2025-11-14	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
941	pedra_branca	2025-11-16	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
942	pedra_branca	2025-11-18	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
943	pedra_branca	2025-11-21	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
944	pedra_branca	2025-11-23	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
945	pedra_branca	2025-11-25	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
946	pedra_branca	2025-11-28	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
947	pedra_branca	2025-11-30	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
948	pedra_branca	2025-12-02	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
949	pedra_branca	2025-12-05	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
950	pedra_branca	2025-12-07	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
951	pedra_branca	2025-12-09	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
952	pedra_branca	2025-12-12	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
953	pedra_branca	2025-12-14	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
954	pedra_branca	2025-12-16	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
955	pedra_branca	2025-12-19	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
956	pedra_branca	2025-12-21	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
957	pedra_branca	2025-12-23	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
958	pedra_branca	2025-12-26	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
959	pedra_branca	2025-12-28	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
960	pedra_branca	2025-12-30	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
961	pedra_branca	2026-01-02	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
962	pedra_branca	2026-01-04	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
963	pedra_branca	2026-01-06	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
964	pedra_branca	2026-01-09	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
965	pedra_branca	2026-01-11	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
966	pedra_branca	2026-01-13	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
967	pedra_branca	2026-01-16	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
968	pedra_branca	2026-01-18	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
969	pedra_branca	2026-01-20	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
970	pedra_branca	2026-01-23	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
971	pedra_branca	2026-01-25	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
972	pedra_branca	2026-01-27	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
973	pedra_branca	2026-01-30	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
974	pedra_branca	2026-02-01	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
975	pedra_branca	2026-02-03	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
976	pedra_branca	2026-02-06	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
977	pedra_branca	2026-02-08	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
978	pedra_branca	2026-02-10	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
979	pedra_branca	2026-02-13	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
980	pedra_branca	2026-02-15	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
981	pedra_branca	2026-02-17	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
982	pedra_branca	2026-02-20	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
983	pedra_branca	2026-02-22	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
984	pedra_branca	2026-02-24	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
985	pedra_branca	2026-02-27	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
986	pedra_branca	2026-03-01	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
987	pedra_branca	2026-03-03	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
988	pedra_branca	2026-03-06	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
989	pedra_branca	2026-03-08	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
990	pedra_branca	2026-03-10	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
991	pedra_branca	2026-03-13	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
992	pedra_branca	2026-03-15	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
993	pedra_branca	2026-03-17	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
994	pedra_branca	2026-03-20	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
995	pedra_branca	2026-03-22	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
996	pedra_branca	2026-03-24	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
997	pedra_branca	2026-03-27	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
998	pedra_branca	2026-03-29	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
999	pedra_branca	2026-03-31	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1000	pedra_branca	2026-04-03	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1001	pedra_branca	2026-04-05	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1002	pedra_branca	2026-04-07	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1003	pedra_branca	2026-04-10	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1004	pedra_branca	2026-04-12	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1005	pedra_branca	2026-04-14	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1006	pedra_branca	2026-04-17	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1007	pedra_branca	2026-04-19	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1008	pedra_branca	2026-04-21	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1009	pedra_branca	2026-04-24	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1010	pedra_branca	2026-04-26	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1011	pedra_branca	2026-04-28	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1012	pedra_branca	2026-05-01	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1013	pedra_branca	2026-05-03	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1014	pedra_branca	2026-05-05	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1015	pedra_branca	2026-05-08	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1016	pedra_branca	2026-05-10	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1017	pedra_branca	2026-05-12	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1018	pedra_branca	2026-05-15	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1019	pedra_branca	2026-05-17	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1020	pedra_branca	2026-05-19	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1021	pedra_branca	2026-05-22	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1022	pedra_branca	2026-05-24	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1023	pedra_branca	2026-05-26	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1024	pedra_branca	2026-05-29	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1025	pedra_branca	2026-05-31	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1026	pedra_branca	2026-06-02	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1027	pedra_branca	2026-06-05	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1028	pedra_branca	2026-06-07	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1029	pedra_branca	2026-06-09	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1030	pedra_branca	2026-06-12	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1031	pedra_branca	2026-06-14	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1032	pedra_branca	2026-06-16	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1033	pedra_branca	2026-06-19	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1034	pedra_branca	2026-06-21	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1035	pedra_branca	2026-06-23	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1036	pedra_branca	2026-06-26	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1037	pedra_branca	2026-06-28	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1038	pedra_branca	2026-06-30	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1039	pedra_branca	2026-07-03	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1040	pedra_branca	2026-07-05	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1041	pedra_branca	2026-07-07	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1042	pedra_branca	2026-07-10	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1043	pedra_branca	2026-07-12	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1044	pedra_branca	2026-07-14	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1045	pedra_branca	2026-07-17	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1046	pedra_branca	2026-07-19	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1047	pedra_branca	2026-07-21	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1048	pedra_branca	2026-07-24	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1049	pedra_branca	2026-07-26	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1050	pedra_branca	2026-07-28	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1051	pedra_branca	2026-07-31	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1052	pedra_branca	2026-08-02	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1053	pedra_branca	2026-08-04	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1054	pedra_branca	2026-08-07	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1055	pedra_branca	2026-08-09	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1056	pedra_branca	2026-08-11	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1057	pedra_branca	2026-08-14	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1058	pedra_branca	2026-08-16	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1059	pedra_branca	2026-08-18	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1060	pedra_branca	2026-08-21	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1061	pedra_branca	2026-08-23	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1062	pedra_branca	2026-08-25	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1063	pedra_branca	2026-08-28	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1064	pedra_branca	2026-08-30	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1065	pedra_branca	2026-09-01	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1066	pedra_branca	2026-09-04	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1067	pedra_branca	2026-09-06	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1068	pedra_branca	2026-09-08	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1069	pedra_branca	2026-09-11	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1070	pedra_branca	2026-09-13	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1071	pedra_branca	2026-09-15	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1072	pedra_branca	2026-09-18	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1073	pedra_branca	2026-09-20	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1074	pedra_branca	2026-09-22	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1075	pedra_branca	2026-09-25	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1076	pedra_branca	2026-09-27	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1077	pedra_branca	2026-09-29	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1078	pedra_branca	2026-10-02	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1079	pedra_branca	2026-10-04	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1080	pedra_branca	2026-10-06	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1081	pedra_branca	2026-10-09	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1082	pedra_branca	2026-10-11	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1083	pedra_branca	2026-10-13	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1084	pedra_branca	2026-10-16	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1085	pedra_branca	2026-10-18	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1086	pedra_branca	2026-10-20	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1087	pedra_branca	2026-10-23	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1088	pedra_branca	2026-10-25	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1089	pedra_branca	2026-10-27	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1090	pedra_branca	2026-10-30	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1091	pedra_branca	2026-11-01	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1092	pedra_branca	2026-11-03	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1093	pedra_branca	2026-11-06	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1094	pedra_branca	2026-11-08	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1095	pedra_branca	2026-11-10	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1096	pedra_branca	2026-11-13	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1097	pedra_branca	2026-11-15	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1098	pedra_branca	2026-11-17	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1099	pedra_branca	2026-11-20	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1100	pedra_branca	2026-11-22	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1101	pedra_branca	2026-11-24	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1102	pedra_branca	2026-11-27	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1103	pedra_branca	2026-11-29	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1104	pedra_branca	2026-12-01	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1105	pedra_branca	2026-12-04	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1106	pedra_branca	2026-12-06	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1107	pedra_branca	2026-12-08	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1108	pedra_branca	2026-12-11	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1109	pedra_branca	2026-12-13	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1110	pedra_branca	2026-12-15	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1111	pedra_branca	2026-12-18	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1112	pedra_branca	2026-12-20	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1113	pedra_branca	2026-12-22	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1114	pedra_branca	2026-12-25	Friday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1115	pedra_branca	2026-12-27	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1116	pedra_branca	2026-12-29	Tuesday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1117	central	2025-10-16	Thursday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1118	central	2025-10-18	Saturday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1119	central	2025-10-19	Sunday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1120	central	2025-10-20	Monday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1121	central	2025-10-23	Thursday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1122	central	2025-10-25	Saturday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1123	central	2025-10-26	Sunday	\N	Celiane	2025-10-26 17:35:08.231323+00	\N
1124	central	2025-10-27	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1125	central	2025-10-30	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1126	central	2025-11-01	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1127	central	2025-11-02	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1128	central	2025-11-03	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1129	central	2025-11-06	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1130	central	2025-11-08	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1131	central	2025-11-09	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1132	central	2025-11-10	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1133	central	2025-11-13	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1134	central	2025-11-15	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1135	central	2025-11-16	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1136	central	2025-11-17	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1137	central	2025-11-20	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1138	central	2025-11-22	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1139	central	2025-11-23	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1140	central	2025-11-24	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1141	central	2025-11-27	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1142	central	2025-11-29	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1143	central	2025-11-30	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1144	central	2025-12-01	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1145	central	2025-12-04	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1146	central	2025-12-06	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1147	central	2025-12-07	Sunday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1148	central	2025-12-08	Monday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1149	central	2025-12-11	Thursday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1150	central	2025-12-13	Saturday	\N	\N	2025-10-26 17:35:08.231323+00	\N
1151	teste	2025-10-19	Sunday	Teste User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1152	teste	2025-10-21	Tuesday	Teste2 User	Teste User	2025-10-26 17:35:08.231323+00	\N
1153	teste	2025-10-26	Sunday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1154	teste	2025-10-28	Tuesday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1155	teste	2025-11-02	Sunday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1156	teste	2025-11-04	Tuesday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1157	teste	2025-11-09	Sunday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1158	teste	2025-11-11	Tuesday	Teste User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1159	teste	2025-11-16	Sunday	Teste User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1160	teste	2025-11-18	Tuesday	Teste2 User	Teste User	2025-10-26 17:35:08.231323+00	\N
1161	teste	2025-11-23	Sunday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1162	teste	2025-11-25	Tuesday	Teste User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1163	teste	2025-11-30	Sunday	Teste2 User	Teste User	2025-10-26 17:35:08.231323+00	\N
1164	teste	2025-12-02	Tuesday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1165	teste	2025-12-07	Sunday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1166	teste	2025-12-09	Tuesday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1167	teste	2025-12-14	Sunday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1168	teste	2025-12-16	Tuesday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1169	teste	2025-12-21	Sunday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1170	teste	2025-12-23	Tuesday	Teste2 User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1171	teste	2025-12-28	Sunday	Teste User	Teste2 User	2025-10-26 17:35:08.231323+00	\N
1172	teste	2025-12-30	Tuesday	Teste User	Teste User	2025-10-26 17:35:08.231323+00	\N
1173	atibaia-jardim	2025-10-23	Thursday	Michelle Freitas Domingues	Michelle Freitas Domingues	2025-10-26 17:35:08.231323+00	\N
1174	atibaia-jardim	2025-10-25	Saturday	Priscila Martinez Silveira Leite	Priscila Martinez Silveira Leite	2025-10-26 17:35:08.231323+00	\N
1175	atibaia-jardim	2025-10-26	Sunday	Eunice Costa Leme	Eunice Costa Leme	2025-10-26 17:35:08.231323+00	\N
1176	atibaia-jardim	2025-10-28	Tuesday	Thaina Fortunato Pinto	Thaina Fortunato Pinto	2025-10-26 17:35:08.231323+00	\N
1177	atibaia-jardim	2025-10-30	Thursday	Luciene Costa Lima	Luciene Costa Lima	2025-10-26 17:35:08.231323+00	\N
1178	atibaia-jardim	2025-11-01	Saturday	Cristiane Oliveira Campezzi de Souza	Cristiane Oliveira Campezzi de Souza	2025-10-26 17:35:08.231323+00	\N
1179	atibaia-jardim	2025-11-02	Sunday	Luci Maziero Alvez	Luci Maziero Alvez	2025-10-26 17:35:08.231323+00	\N
1180	atibaia-jardim	2025-11-04	Tuesday	Claudia	Claudia	2025-10-26 17:35:08.231323+00	\N
1181	atibaia-jardim	2025-11-06	Thursday	Claudia	Claudia	2025-10-26 17:35:08.231323+00	\N
1182	atibaia-jardim	2025-11-08	Saturday	Irene Candido Amorim	Irene Candido Amorim	2025-10-26 17:35:08.231323+00	\N
1183	atibaia-jardim	2025-11-09	Sunday	Ariana Guimaraes Francisco	Ariana Guimaraes Francisco	2025-10-26 17:35:08.231323+00	\N
1184	atibaia-jardim	2025-11-11	Tuesday	Cristiane Oliveira Campezzi de Souza	Cristiane Oliveira Campezzi de Souza	2025-10-26 17:35:08.231323+00	\N
1185	atibaia-jardim	2025-11-13	Thursday	Ana Paula Freitas Domingues	Ana Paula Freitas Domingues	2025-10-26 17:35:08.231323+00	\N
1186	atibaia-jardim	2025-11-15	Saturday	Giovana Passos Polessi	Giovana Passos Polessi	2025-10-26 17:35:08.231323+00	\N
1187	atibaia-jardim	2025-11-16	Sunday	Michelle Freitas Domingues	Michelle Freitas Domingues	2025-10-26 17:35:08.231323+00	\N
1188	atibaia-jardim	2025-11-18	Tuesday	Ariana Guimaraes Francisco	Ariana Guimaraes Francisco	2025-10-26 17:35:08.231323+00	\N
1189	atibaia-jardim	2025-11-20	Thursday	Adriana da Silva Frias Pereira	Adriana da Silva Frias Pereira	2025-10-26 17:35:08.231323+00	\N
1190	atibaia-jardim	2025-11-22	Saturday	Eunice Costa Leme	Eunice Costa Leme	2025-10-26 17:35:08.231323+00	\N
1191	atibaia-jardim	2025-11-23	Sunday	Luciene Costa Lima	Luciene Costa Lima	2025-10-26 17:35:08.231323+00	\N
1192	atibaia-jardim	2025-11-25	Tuesday	Thaina Fortunato Pinto	Thaina Fortunato Pinto	2025-10-26 17:35:08.231323+00	\N
1193	atibaia-jardim	2025-11-27	Thursday	Priscila Martinez Silveira Leite	Priscila Martinez Silveira Leite	2025-10-26 17:35:08.231323+00	\N
1194	atibaia-jardim	2025-11-29	Saturday	Luci Maziero Alvez	Luci Maziero Alvez	2025-10-26 17:35:08.231323+00	\N
1195	atibaia-jardim	2025-11-30	Sunday	Claudia	Claudia	2025-10-26 17:35:08.231323+00	\N
1196	atibaia-jardim	2025-12-02	Tuesday	Irene Candido Amorim	Irene Candido Amorim	2025-10-26 17:35:08.231323+00	\N
1197	atibaia-jardim	2025-12-04	Thursday	Cristiane Oliveira Campezzi de Souza	Cristiane Oliveira Campezzi de Souza	2025-10-26 17:35:08.231323+00	\N
1198	atibaia-jardim	2025-12-06	Saturday	Ariana Guimaraes Francisco	Ariana Guimaraes Francisco	2025-10-26 17:35:08.231323+00	\N
1199	atibaia-jardim	2025-12-07	Sunday	Ana Paula Freitas Domingues	Ana Paula Freitas Domingues	2025-10-26 17:35:08.231323+00	\N
1200	atibaia-jardim	2025-12-09	Tuesday	Cristiane Oliveira Campezzi de Souza	Cristiane Oliveira Campezzi de Souza	2025-10-26 17:35:08.231323+00	\N
1201	atibaia-jardim	2025-12-11	Thursday	Irene Candido Amorim	Irene Candido Amorim	2025-10-26 17:35:08.231323+00	\N
1202	atibaia-jardim	2025-12-13	Saturday	Michelle Freitas Domingues	Michelle Freitas Domingues	2025-10-26 17:35:08.231323+00	\N
1203	atibaia-jardim	2025-12-14	Sunday	Adriana da Silva Frias Pereira	Adriana da Silva Frias Pereira	2025-10-26 17:35:08.231323+00	\N
1204	atibaia-jardim	2025-12-16	Tuesday	Claudia	Claudia	2025-10-26 17:35:08.231323+00	\N
1205	atibaia-jardim	2025-12-18	Thursday	Giovana Passos Polessi	Giovana Passos Polessi	2025-10-26 17:35:08.231323+00	\N
1206	atibaia-jardim	2025-12-20	Saturday	Luciene Costa Lima	Luciene Costa Lima	2025-10-26 17:35:08.231323+00	\N
1207	atibaia-jardim	2025-12-21	Sunday	Priscila Martinez Silveira Leite	Priscila Martinez Silveira Leite	2025-10-26 17:35:08.231323+00	\N
1208	atibaia-jardim	2025-12-23	Tuesday	Thaina Fortunato Pinto	Thaina Fortunato Pinto	2025-10-26 17:35:08.231323+00	\N
1209	atibaia-jardim	2025-12-25	Thursday	Eunice Costa Leme	Eunice Costa Leme	2025-10-26 17:35:08.231323+00	\N
1210	atibaia-jardim	2025-12-27	Saturday	Claudia	Claudia	2025-10-26 17:35:08.231323+00	\N
1211	atibaia-jardim	2025-12-28	Sunday	Luci Maziero Alvez	Luci Maziero Alvez	2025-10-26 17:35:08.231323+00	\N
1212	atibaia-jardim	2025-12-30	Tuesday	Ariana Guimaraes Francisco	Ariana Guimaraes Francisco	2025-10-26 17:35:08.231323+00	\N
\.


--
-- Data for Name: escala_publicacao; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.escala_publicacao (comum_id, publicada_em, publicada_por, periodo_inicio, periodo_fim) FROM stdin;
\.


--
-- Data for Name: escala_rjm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.escala_rjm (id, comum_id, data, dia_semana, organista, criado_em, criado_por) FROM stdin;
rjm_9	vila_paula	2025-12-14	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_10	vila_paula	2025-12-21	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_11	vila_paula	2025-12-28	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_12	vila_paula	2026-01-04	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_13	vila_paula	2026-01-11	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_14	vila_paula	2026-01-18	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_15	vila_paula	2026-01-25	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_16	vila_paula	2026-02-01	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_17	vila_paula	2026-02-08	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_18	pedra_branca	2026-02-15	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_19	pedra_branca	2026-02-22	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_20	pedra_branca	2026-03-01	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_21	pedra_branca	2026-03-08	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_22	pedra_branca	2026-03-15	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_23	pedra_branca	2026-03-22	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_24	pedra_branca	2026-03-29	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_25	pedra_branca	2026-04-05	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_26	pedra_branca	2026-04-12	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_27	pedra_branca	2026-04-19	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_28	pedra_branca	2026-04-26	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_29	pedra_branca	2026-05-03	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_30	pedra_branca	2026-05-10	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_31	pedra_branca	2026-05-17	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_32	pedra_branca	2026-05-24	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_33	pedra_branca	2026-05-31	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_34	pedra_branca	2026-06-07	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_35	pedra_branca	2026-06-14	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_36	pedra_branca	2026-06-21	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_37	pedra_branca	2026-06-28	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_38	pedra_branca	2026-07-05	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_39	pedra_branca	2026-07-12	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_40	pedra_branca	2026-07-19	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_41	pedra_branca	2026-07-26	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_42	pedra_branca	2026-08-02	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_43	pedra_branca	2026-08-09	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_44	pedra_branca	2026-08-16	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_45	pedra_branca	2026-08-23	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_46	pedra_branca	2026-08-30	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_47	pedra_branca	2026-09-06	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_48	pedra_branca	2026-09-13	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_49	pedra_branca	2026-09-20	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_50	pedra_branca	2026-09-27	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_51	pedra_branca	2026-10-04	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_52	pedra_branca	2026-10-11	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_53	pedra_branca	2026-10-18	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_54	pedra_branca	2026-10-25	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_55	pedra_branca	2026-11-01	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_56	pedra_branca	2026-11-08	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_57	pedra_branca	2026-11-15	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_58	pedra_branca	2026-11-22	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_59	pedra_branca	2026-11-29	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_60	pedra_branca	2026-12-06	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_61	pedra_branca	2026-12-13	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_62	pedra_branca	2026-12-20	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_63	pedra_branca	2026-12-27	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_1	vila_paula	2025-10-19	Sunday	Celiane	2025-10-26 17:35:08.231323+00	\N
rjm_2	vila_paula	2025-10-26	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_3	vila_paula	2025-11-02	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_4	vila_paula	2025-11-09	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_5	vila_paula	2025-11-16	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_6	vila_paula	2025-11-23	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_7	vila_paula	2025-11-30	Sunday		2025-10-26 17:35:08.231323+00	\N
rjm_8	vila_paula	2025-12-07	Sunday		2025-10-26 17:35:08.231323+00	\N
\.


--
-- Data for Name: indisponibilidades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.indisponibilidades (id, comum_id, organista_id, data, motivo, autor, status, created_at) FROM stdin;
19	vila_paula	janaina	2025-10-20	Indisponível	janaina	confirmada	2025-10-26 17:35:08.226508+00
20	vila_paula	janaina	2025-11-10	Indisponível	janaina	confirmada	2025-10-26 17:35:08.226508+00
21	vila_paula	raquel	2025-10-13	Indisponível	raquel	confirmada	2025-10-26 17:35:08.226508+00
22	vila_paula	raquel	2025-11-10	Indisponível	raquel	confirmada	2025-10-26 17:35:08.226508+00
23	vila_paula	milena	2025-10-22	Indisponível	milena	confirmada	2025-10-26 17:35:08.226508+00
24	vila_paula	milena	2025-11-17	Indisponível	milena	confirmada	2025-10-26 17:35:08.226508+00
\.


--
-- Data for Name: logs_auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.logs_auditoria (id, "timestamp", tipo, categoria, acao, descricao, usuario_id, usuario_nome, usuario_tipo, regional_id, sub_regional_id, comum_id, status, ip, user_agent, dados_antes, dados_depois) FROM stdin;
8c65c8df-8079-4c44-8873-22b95315ae1b	2025-10-23 19:30:17.67326+00	login	autenticacao	login_sucesso	Login realizado com sucesso	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
024e7ab3-d8f5-422a-9a37-9e92eab2c46f	2025-10-23 19:50:01.442696+00	logout	autenticacao	logout	Usuário realizou logout	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
abdec5b2-ab7a-48d8-b3a5-4d9e1d0ef1bf	2025-10-23 19:50:12.356648+00	login	autenticacao	login_sucesso	Login realizado com sucesso (organista)	thaina.fortunato	Thaina Fortunato Pinto	organista	atibaia	sub-atibaia	atibaia-jardim	sucesso	172.22.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
1ab17446-d946-4a1c-9e01-8822dfdf85ab	2025-10-23 19:51:11.156175+00	logout	autenticacao	logout	Usuário realizou logout	thaina.fortunato	Thaina Fortunato Pinto	organista	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
a5f6e09d-fdec-468b-aff1-d1f8a5e8288d	2025-10-23 19:51:26.818836+00	login	autenticacao	login_sucesso	Login realizado com sucesso	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
32a790a1-296f-44ab-9092-f19f2dce38c6	2025-10-23 20:07:12.786967+00	login	autenticacao	login_sucesso	Login realizado com sucesso	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36	\N	\N
d713cbf1-e2b3-4835-bbb5-7a71be9b319d	2025-10-23 20:15:54.106051+00	login	autenticacao	login_falha	Tentativa de login falhou para usuário: enc_atiabaiajardim	enc_atiabaiajardim	enc_atiabaiajardim	desconhecido	\N	\N	\N	falha	172.22.0.3	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/130.0.0.0 Mobile Safari/537.36	\N	\N
8e5ed5e6-965c-408d-81fa-905edf206777	2025-10-23 20:16:14.62721+00	login	autenticacao	login_sucesso	Login realizado com sucesso	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.22.0.3	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/130.0.0.0 Mobile Safari/537.36	\N	\N
e87f15b4-4298-4869-a81f-9902c83efbac	2025-10-24 13:01:41.019222+00	logout	autenticacao	logout	Usuário realizou logout	enc_atibaiajardim	Alan Campezzi	encarregado_comum	\N	\N	\N	sucesso	172.23.0.3	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36	\N	\N
f7cd41cd-0acc-4f5a-88d7-fbdfde6d47da	2025-10-25 12:25:29.326649+00	login	autenticacao	login_sucesso	Login realizado com sucesso (organista)	ieda	Ieda	organista	gru	santa_isabel	vila_paula	sucesso	172.23.0.3	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36	\N	\N
\.


--
-- Data for Name: organista_dias_permitidos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organista_dias_permitidos (organista_id, dia) FROM stdin;
yasminc	Domingo
yasming	Domingo
milena	Domingo
milena	Terça
ieda	Domingo
ieda	Terça
raquel	Domingo
janaina	Domingo
celiane	Domingo
celiane	Segunda
celiane	Quinta
celiane	Sábado
graciela	Terça
graciela	Sexta
victoria	Terça
victoria	Sexta
teste	Domingo
teste	Terça
teste2	Domingo
teste2	Terça
adriana.pereira	Domingo
adriana.pereira	Terça
adriana.pereira	Quinta
adriana.pereira	Sábado
ana.domingues	Domingo
ana.domingues	Terça
ana.domingues	Quinta
ana.domingues	Sábado
ariana.francisco	Domingo
ariana.francisco	Terça
ariana.francisco	Quinta
ariana.francisco	Sábado
cristiane.souza	Domingo
cristiane.souza	Terça
cristiane.souza	Quinta
cristiane.souza	Sábado
eunice.leme	Domingo
eunice.leme	Terça
eunice.leme	Quinta
eunice.leme	Sábado
giovana.polessi	Domingo
giovana.polessi	Terça
giovana.polessi	Quinta
giovana.polessi	Sábado
irene.amorim	Domingo
irene.amorim	Terça
irene.amorim	Quinta
irene.amorim	Sábado
luci.alvez	Domingo
luci.alvez	Terça
luci.alvez	Quinta
luci.alvez	Sábado
luciene.lima	Domingo
luciene.lima	Terça
luciene.lima	Quinta
luciene.lima	Sábado
michelle.domingues	Domingo
michelle.domingues	Terça
michelle.domingues	Quinta
michelle.domingues	Sábado
priscila.leite	Domingo
priscila.leite	Terça
priscila.leite	Quinta
priscila.leite	Sábado
thaina.fortunato	Domingo
thaina.fortunato	Terça
thaina.fortunato	Quinta
thaina.fortunato	Sábado
claudia.atibaiajardim	Domingo
claudia.atibaiajardim	Terça
claudia.atibaiajardim	Quinta
claudia.atibaiajardim	Sábado
\.


--
-- Data for Name: organista_regras_especiais; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organista_regras_especiais (organista_id, chave, valor) FROM stdin;
\.


--
-- Data for Name: organista_tipos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organista_tipos (organista_id, tipo) FROM stdin;
yasminc	Meia-hora
yasminc	RJM
yasming	Meia-hora
milena	Meia-hora
milena	Culto
milena	RJM
ieda	Meia-hora
ieda	Culto
raquel	Culto
janaina	Culto
celiane	Culto
celiane	RJM
graciela	Meia-hora
graciela	Culto
victoria	Meia-hora
victoria	Culto
teste	Meia-hora
teste	Culto
teste	RJM
teste2	Meia-hora
teste2	Culto
teste2	RJM
adriana.pereira	Meia-hora
adriana.pereira	Culto
ana.domingues	Meia-hora
ana.domingues	Culto
ariana.francisco	Meia-hora
ariana.francisco	Culto
cristiane.souza	Meia-hora
cristiane.souza	Culto
eunice.leme	Meia-hora
eunice.leme	Culto
giovana.polessi	Meia-hora
giovana.polessi	Culto
irene.amorim	Meia-hora
irene.amorim	Culto
luci.alvez	Meia-hora
luci.alvez	Culto
luciene.lima	Meia-hora
luciene.lima	Culto
michelle.domingues	Meia-hora
michelle.domingues	Culto
michelle.domingues	RJM
priscila.leite	Meia-hora
priscila.leite	Culto
thaina.fortunato	Meia-hora
thaina.fortunato	Culto
claudia.atibaiajardim	Meia-hora
claudia.atibaiajardim	Culto
\.


--
-- Data for Name: organistas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organistas (id, comum_id, nome, password_hash, created_at, updated_at) FROM stdin;
yasminc	vila_paula	Yasmin C.	scrypt:32768:8:1$LQHPQ0sO9i4R4gEo$341f6a9bf71ddcc9a2af7e0415574668b8e3a508f7913e1fcafc864e716a698bdd5ecad4f81d8840ce8b240977342bf6cd4b66f4a27de7be5f3c40b2be4fdc1f	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
yasming	vila_paula	Yasmin G.	scrypt:32768:8:1$ARQexKTwY8Je6a8u$25229a357358835faf3e643550875883ee9800fb69f9755e3da4d36c06aa28ad44534557d529f164a9453e3215c6e584c3826a3e836fa083a7e685baa14985f9	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
milena	vila_paula	Milena	scrypt:32768:8:1$OnTtwVUzOjrpVCyh$9b3f0dcdbeda061418108201cfdacff8dc11b24884d63b01c7581c4ed368fdec0af4c6402e0ab864b7097d2d3dad85490dfe67382bea72b1a5c7bf820b9ee8f2	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
ieda	vila_paula	Ieda	scrypt:32768:8:1$gV4dH9K4e6JDED6U$a0c5b030cb48b5a5b72d9f8e853195f23ef876509ad5f1fdb830055915d41fc31edfaac6b673de874ed1b5cc7012431a2f87dd3dfe492812941c3437f13ff7cd	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
raquel	vila_paula	Raquel	scrypt:32768:8:1$Ge0pIG8Cx5O20f3W$c57889310cfc1afd4fbbb49500f0f6a125b7077fb30821a57c5bbe940bd60265d6c177e0a933220b638f2c4ed8e866c17167acc612c693e2513a32c53d7a801c	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
janaina	vila_paula	Janaina	scrypt:32768:8:1$wFzc3PFcaUFoeHuT$519897bb7b33d71adf762eee92796721d3d79187a2aec1dd2d55f8402ee8b4a3874b9fc4f8ea6f75b587135e39cc3b846bbe6b9401b3e442c3e2d984724c67da	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
celiane	central	Celiane	scrypt:32768:8:1$RwRXDsANmucWfyiZ$dc926ba4d38eb818f1c094a111f971c8309b5474e03f032351235643ff79fa5f3d1963b6ba398f5ba1329427080b5764995b80b6ae9a5b0d9ceb12dccff1605f	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
graciela	pedra_branca	Graciela	scrypt:32768:8:1$wQVlszU1cyN1zeZe$aa02a79a9a73c7321e03c23e92f27acc956bac27ce6c779096d5404362f0373e4c2fbe91ebd85963986359146bd0e639039f0ca51ef352101e0b642349fa50eb	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
victoria	pedra_branca	Victoria	scrypt:32768:8:1$NFKK2QNTizwtcpXd$f556b4fe8314bfbfdca83918961dceb5bb4961e9e32d2464bf7502dab2b19b469da6b9600293e195ab51d1fcab76d69c6f798896064a08e8aea16c95cb25518f	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
teste	teste	Teste User	scrypt:32768:8:1$KZSxSsM2tgXDjh56$23ccb6e9da5361b52673e52b6b1173a167d988fe22c1bea49b9d946fe1a0f09d9c07d453c918ee8b5901d95d1f8e070adcba93d7fa3e82f0691be877db0ff152	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
teste2	teste	Teste2 User	scrypt:32768:8:1$JRQxhITyzvIr2XW4$08b85ce096c62a37c850632b64f66eeb30d19a534c980594793bccc06329123d8d9ec9a991bcb3fafca99db2cf8c57f22b7124910c954d7f6ca0bf958ac1be4d	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
adriana.pereira	atibaia-jardim	Adriana da Silva Frias Pereira	scrypt:32768:8:1$vIkbHLORN1nqEDTn$8707e1bb7f22bbb2571ec77546af4c4f2b72ed25f8b5082e0399300d80a92a7040a0e7cbfd256b6e4a159eb714295f9b6c020fb77451d1f60d253f4225984bb7	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
ana.domingues	atibaia-jardim	Ana Paula Freitas Domingues	scrypt:32768:8:1$el0uwIXdX78uM08t$88522b88f2ae53069f74288ce59cd0b983bb7a05d3fde28ef957ed8605d39fedb7267938e6788d129bcee0ce71fe8464b235add64b76c55a97d06b61e5e93471	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
ariana.francisco	atibaia-jardim	Ariana Guimaraes Francisco	scrypt:32768:8:1$7HzPKwjHhmgFBJIA$cb455a7a5278dac5dec954240267037bcaea5518f2b9ff62c0d3802070e0efa664e46ebb53db8ce8a4fa7739307e3248208cbc006785ce02e142d432327a6acd	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
cristiane.souza	atibaia-jardim	Cristiane Oliveira Campezzi de Souza	scrypt:32768:8:1$qDlCRdeVwoIvmOQk$73d7fe066bc84b2dcccbb7ee7645faacec2fcf7ff87d195b4487ca3bbbf2ff1f78d48af7ca29e237b70353a2ce00b0fe424008f0f4970ee5c1323cde8482bffa	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
eunice.leme	atibaia-jardim	Eunice Costa Leme	scrypt:32768:8:1$EW9xQWsp4b5trpfg$b1d9303a8ac0844cb9d11728fc63785c54d5beb8ab532b6732f698b59831ecb4816e36cc5fc2d8745312d0f2fe6ae12dab72910e6441023d2a6ae4a0440fe453	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
giovana.polessi	atibaia-jardim	Giovana Passos Polessi	scrypt:32768:8:1$VQ9ybFuiBJt4wRvD$ba4569551c77e93e223a6e21571502f3229a5f430decf81e1b6cc41df1af27a106956a546d83f198c469defd2486495b0e293168107d6e628e42b8e60e7b5c01	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
irene.amorim	atibaia-jardim	Irene Candido Amorim	scrypt:32768:8:1$5CYh3HQYI5SYNuLg$a679d888bef7e21b2fdcfff1b2d38de6cdb3c16a8f923d219f12f4c2d748ad153fbf529439e641e97109c7ffd9b253a58474b6ca28453b13188dd268928524b1	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
luci.alvez	atibaia-jardim	Luci Maziero Alvez	scrypt:32768:8:1$DbQCDAcc4dH38fel$43e6e43a4a1bcf0ac17ee89dfd9f541897de7a1179c44bfded866c13b11a273f0c40f0cfa67a18d67da948857b87596091cdd6b78a1996f6f61eb2e5c82d2583	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
luciene.lima	atibaia-jardim	Luciene Costa Lima	scrypt:32768:8:1$es71ExKbMEogFWr5$46edb0d249e8b5f4bb47b8f10bdf55ed1a244cf06a535a02939df5fa13c8c06324fe3cc9291622c5b0639e85ed2512e6ecfade848c2b3a55af60da339cbbaf60	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
michelle.domingues	atibaia-jardim	Michelle Freitas Domingues	scrypt:32768:8:1$9Y1lpEikAI4tsQUn$4245d391f9b70a7f02f55c0dff5c9f786c5d2152f2dd0bcd9c4152b00e7c04a77a57866e820184597212b44e96682405235d45430a745d982d0df278c05622e4	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
priscila.leite	atibaia-jardim	Priscila Martinez Silveira Leite	scrypt:32768:8:1$zA0Ix9EblM7I5eDc$a2dde057fa3814648c898983ba3474f2319630d114356e5a4fe0145bd2b62e0e9ab96137b68f463979f0721bf31a356f35ba00a3a7c27f9c1deebc3909cd7314	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
thaina.fortunato	atibaia-jardim	Thaina Fortunato Pinto	scrypt:32768:8:1$EClle0N1it82waoh$f9d3d06866c8906d414dfd63480f4cbb8d06e5e99bd4046315d2608e6bab001350a6f24e0b526df044eefc412d7519011a2866594184edd005d754d59d6d1d0c	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
claudia.atibaiajardim	atibaia-jardim	Claudia	scrypt:32768:8:1$nF3oIwqAx8eyBvXW$9574c6da1346db3e1f9577de438a6c59c08924463142b62c3e63ffb08714a110e90321164244dde843093fb8e811ab6b273a2dac14fe50a242b0d9b2541f106e	2025-10-26 17:33:29.861531+00	2025-10-26 17:35:08.186086+00
\.


--
-- Data for Name: regionais; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regionais (id, nome, ativo, created_at, updated_at) FROM stdin;
gru	Regional GRU	t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
atibaia	Atibaia	t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
\.


--
-- Data for Name: sub_regionais; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sub_regionais (id, regional_id, nome, ativo, created_at, updated_at) FROM stdin;
santa_isabel	gru	Sub-Regional Santa Isabel	t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
sub-atibaia	atibaia	Atibaia	t	2025-10-26 17:33:29.853497+00	2025-10-26 17:35:08.177827+00
\.


--
-- Data for Name: trocas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trocas (id, comum_id, status, modalidade, tipo, data, slot, solicitante_id, solicitante_nome, alvo_id, alvo_nome, motivo, criado_em, atualizado_em) FROM stdin;
\.


--
-- Data for Name: trocas_historico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trocas_historico (id, troca_id, quando, acao, por) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, nome, password_hash, tipo, nivel, contexto_id, ativo, created_at, updated_at) FROM stdin;
admin_master	Administrador	scrypt:32768:8:1$IlMxGehI5XW2C6Q5$cde3a7769b678b9f0dc5022f261855ba71e7974fe506425125250ca40413667de5256c2084a8700ad1096f7a8ac6e39cd642f33363b844f651edbbf5ce40fc72	master	sistema	\N	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
enc_pedrabranca	Douglas	scrypt:32768:8:1$iGVUQCY50z3hu6Tq$21925fcc962e7b1d5a0e8f86af5a2685e824cfe750a7e7982002af0c079825a0aaa4593fdb57079cef17af6dd0e2be0bd5867fb61384496dcf67fe0128881e0d	encarregado_comum	comum	pedra_branca	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
enc_central	Felipe	scrypt:32768:8:1$PQYyaKVvZbkj9o9R$7901405b586d54e4c1162312fb59ed0180472e41a95ac7a9c4af2a5922a434b8655cd3ef9c7da4723c082d51cf77800c098896bca38d5ae3b61536232faea28f	encarregado_comum	comum	central	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
alaor	Alaor Rodrigues	scrypt:32768:8:1$eyrDJAWUaIJhS2q8$3a9c798b827b53fe4a774dc6feee17eb9e354d226cf9c47101f94a2dc7dcb53daf9a1a8fd75e49c4cf2662f6e0f6c4f3603ef1eacae4440f8645ee87319878f9	master	sistema		t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
lucas	Lucas	scrypt:32768:8:1$NazbxqDbJnbuygEb$dca5f50784c6a809a250c4bbecc75434776ac7949dfd990c92151f70235c9229b1620343acf15297e9569912aba2afb1dcd38307d810166b56b84d739fe178c1	admin_regional	regional	gru	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
rafael	Rafael	scrypt:32768:8:1$QUf0jnGic1ityk2s$83efd168244d520640b2788abf5f25b878fef8a129eb09a9863d38dc0f2954ca32e8f6532b6861ce7d7ca746c8345095c658b1c6b6264967ef24353a03a35773	admin_regional	regional	gru	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
enc_vilapaula	Alaor Rodrigues	scrypt:32768:8:1$AReH804wHbrZpsbh$d70078bd687786b21fbe2a9a1b691412488d1b890e5445c85350a65905d3d7bad49cf42b596037365c270c20e607e911696c5a7d8d20f543a7e5390260108e5f	encarregado_comum	comum	vila_paula	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
enc_teste	Teste	scrypt:32768:8:1$cAx6JEQVXjOwwKrP$ed066c91e09d1dcd8c7d8f40b3e0832a52d4332bd50e7e1543c2ea29672992479c1d0647b2ec461c9b15a1f27f70ca2c7c505ae834ad5f58d24ec20025c83bf1	encarregado_comum	comum	teste	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
enc_atibaiajardim	Alan Campezzi	scrypt:32768:8:1$4UjkTQzKkzjXCu6h$9c0908e384235c830560b7cc64a034cf228dc906cd03889252c0e8b5844d68b0269439823bfea4c253b1dfd6b44200be9cb2e2c8b72eec8ca1abb1a923a6590d	encarregado_comum	comum	atibaia-jardim	t	2025-10-26 17:35:08.322445+00	2025-10-26 17:35:08.322445+00
\.


--
-- Name: comum_horarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comum_horarios_id_seq', 1, false);


--
-- Name: escala_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.escala_id_seq', 1212, true);


--
-- Name: indisponibilidades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.indisponibilidades_id_seq', 24, true);


--
-- Name: trocas_historico_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trocas_historico_id_seq', 1, false);


--
-- Name: comum_config comum_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_config
    ADD CONSTRAINT comum_config_pkey PRIMARY KEY (comum_id);


--
-- Name: comum_horarios comum_horarios_comum_id_dia_semana_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_horarios
    ADD CONSTRAINT comum_horarios_comum_id_dia_semana_key UNIQUE (comum_id, dia_semana);


--
-- Name: comum_horarios comum_horarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_horarios
    ADD CONSTRAINT comum_horarios_pkey PRIMARY KEY (id);


--
-- Name: comuns comuns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comuns
    ADD CONSTRAINT comuns_pkey PRIMARY KEY (id);


--
-- Name: escala escala_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala
    ADD CONSTRAINT escala_pkey PRIMARY KEY (id);


--
-- Name: escala_publicacao escala_publicacao_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala_publicacao
    ADD CONSTRAINT escala_publicacao_pkey PRIMARY KEY (comum_id);


--
-- Name: escala_rjm escala_rjm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala_rjm
    ADD CONSTRAINT escala_rjm_pkey PRIMARY KEY (id);


--
-- Name: indisponibilidades indisponibilidades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.indisponibilidades
    ADD CONSTRAINT indisponibilidades_pkey PRIMARY KEY (id);


--
-- Name: logs_auditoria logs_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logs_auditoria
    ADD CONSTRAINT logs_auditoria_pkey PRIMARY KEY (id);


--
-- Name: organista_dias_permitidos organista_dias_permitidos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_dias_permitidos
    ADD CONSTRAINT organista_dias_permitidos_pkey PRIMARY KEY (organista_id, dia);


--
-- Name: organista_regras_especiais organista_regras_especiais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_regras_especiais
    ADD CONSTRAINT organista_regras_especiais_pkey PRIMARY KEY (organista_id, chave);


--
-- Name: organista_tipos organista_tipos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_tipos
    ADD CONSTRAINT organista_tipos_pkey PRIMARY KEY (organista_id, tipo);


--
-- Name: organistas organistas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organistas
    ADD CONSTRAINT organistas_pkey PRIMARY KEY (id);


--
-- Name: regionais regionais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regionais
    ADD CONSTRAINT regionais_pkey PRIMARY KEY (id);


--
-- Name: sub_regionais sub_regionais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sub_regionais
    ADD CONSTRAINT sub_regionais_pkey PRIMARY KEY (id);


--
-- Name: trocas_historico trocas_historico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trocas_historico
    ADD CONSTRAINT trocas_historico_pkey PRIMARY KEY (id);


--
-- Name: trocas trocas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trocas
    ADD CONSTRAINT trocas_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: idx_escala_comum_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_escala_comum_data ON public.escala USING btree (comum_id, data);


--
-- Name: idx_escala_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_escala_data ON public.escala USING btree (data);


--
-- Name: idx_escala_rjm_comum_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_escala_rjm_comum_data ON public.escala_rjm USING btree (comum_id, data);


--
-- Name: idx_indisponibilidades_comum_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_indisponibilidades_comum_data ON public.indisponibilidades USING btree (comum_id, data);


--
-- Name: idx_indisponibilidades_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_indisponibilidades_data ON public.indisponibilidades USING btree (data);


--
-- Name: idx_indisponibilidades_organista; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_indisponibilidades_organista ON public.indisponibilidades USING btree (organista_id);


--
-- Name: idx_logs_comum; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_logs_comum ON public.logs_auditoria USING btree (comum_id);


--
-- Name: idx_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_logs_timestamp ON public.logs_auditoria USING btree ("timestamp" DESC);


--
-- Name: idx_logs_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_logs_usuario ON public.logs_auditoria USING btree (usuario_id);


--
-- Name: idx_organistas_comum; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_organistas_comum ON public.organistas USING btree (comum_id);


--
-- Name: idx_trocas_comum_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trocas_comum_status ON public.trocas USING btree (comum_id, status);


--
-- Name: idx_trocas_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trocas_data ON public.trocas USING btree (data);


--
-- Name: idx_usuarios_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_tipo ON public.usuarios USING btree (tipo);


--
-- Name: comum_config update_comum_config_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_comum_config_updated_at BEFORE UPDATE ON public.comum_config FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: comuns update_comuns_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_comuns_updated_at BEFORE UPDATE ON public.comuns FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: organistas update_organistas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_organistas_updated_at BEFORE UPDATE ON public.organistas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: regionais update_regionais_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_regionais_updated_at BEFORE UPDATE ON public.regionais FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: sub_regionais update_sub_regionais_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_sub_regionais_updated_at BEFORE UPDATE ON public.sub_regionais FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: trocas update_trocas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_trocas_updated_at BEFORE UPDATE ON public.trocas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: usuarios update_usuarios_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: comum_config comum_config_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_config
    ADD CONSTRAINT comum_config_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: comum_horarios comum_horarios_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comum_horarios
    ADD CONSTRAINT comum_horarios_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: comuns comuns_sub_regional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comuns
    ADD CONSTRAINT comuns_sub_regional_id_fkey FOREIGN KEY (sub_regional_id) REFERENCES public.sub_regionais(id) ON DELETE CASCADE;


--
-- Name: escala escala_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala
    ADD CONSTRAINT escala_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: escala_publicacao escala_publicacao_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala_publicacao
    ADD CONSTRAINT escala_publicacao_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: escala_rjm escala_rjm_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.escala_rjm
    ADD CONSTRAINT escala_rjm_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: indisponibilidades indisponibilidades_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.indisponibilidades
    ADD CONSTRAINT indisponibilidades_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: indisponibilidades indisponibilidades_organista_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.indisponibilidades
    ADD CONSTRAINT indisponibilidades_organista_id_fkey FOREIGN KEY (organista_id) REFERENCES public.organistas(id) ON DELETE CASCADE;


--
-- Name: organista_dias_permitidos organista_dias_permitidos_organista_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_dias_permitidos
    ADD CONSTRAINT organista_dias_permitidos_organista_id_fkey FOREIGN KEY (organista_id) REFERENCES public.organistas(id) ON DELETE CASCADE;


--
-- Name: organista_regras_especiais organista_regras_especiais_organista_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_regras_especiais
    ADD CONSTRAINT organista_regras_especiais_organista_id_fkey FOREIGN KEY (organista_id) REFERENCES public.organistas(id) ON DELETE CASCADE;


--
-- Name: organista_tipos organista_tipos_organista_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organista_tipos
    ADD CONSTRAINT organista_tipos_organista_id_fkey FOREIGN KEY (organista_id) REFERENCES public.organistas(id) ON DELETE CASCADE;


--
-- Name: organistas organistas_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organistas
    ADD CONSTRAINT organistas_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: sub_regionais sub_regionais_regional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sub_regionais
    ADD CONSTRAINT sub_regionais_regional_id_fkey FOREIGN KEY (regional_id) REFERENCES public.regionais(id) ON DELETE CASCADE;


--
-- Name: trocas trocas_comum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trocas
    ADD CONSTRAINT trocas_comum_id_fkey FOREIGN KEY (comum_id) REFERENCES public.comuns(id) ON DELETE CASCADE;


--
-- Name: trocas_historico trocas_historico_troca_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trocas_historico
    ADD CONSTRAINT trocas_historico_troca_id_fkey FOREIGN KEY (troca_id) REFERENCES public.trocas(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO rodizio_user;


--
-- Name: FUNCTION gtrgm_in(cstring); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_in(cstring) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_out(public.gtrgm); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_out(public.gtrgm) TO rodizio_user;


--
-- Name: FUNCTION gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gin_extract_query_trgm(text, internal, smallint, internal, internal, internal, internal) TO rodizio_user;


--
-- Name: FUNCTION gin_extract_value_trgm(text, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gin_extract_value_trgm(text, internal) TO rodizio_user;


--
-- Name: FUNCTION gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gin_trgm_consistent(internal, smallint, text, integer, internal, internal, internal, internal) TO rodizio_user;


--
-- Name: FUNCTION gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gin_trgm_triconsistent(internal, smallint, text, integer, internal, internal, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_compress(internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_compress(internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_consistent(internal, text, smallint, oid, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_consistent(internal, text, smallint, oid, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_decompress(internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_decompress(internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_distance(internal, text, smallint, oid, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_distance(internal, text, smallint, oid, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_options(internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_options(internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_penalty(internal, internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_penalty(internal, internal, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_picksplit(internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_picksplit(internal, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_same(public.gtrgm, public.gtrgm, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_same(public.gtrgm, public.gtrgm, internal) TO rodizio_user;


--
-- Name: FUNCTION gtrgm_union(internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gtrgm_union(internal, internal) TO rodizio_user;


--
-- Name: FUNCTION set_limit(real); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.set_limit(real) TO rodizio_user;


--
-- Name: FUNCTION show_limit(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.show_limit() TO rodizio_user;


--
-- Name: FUNCTION show_trgm(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.show_trgm(text) TO rodizio_user;


--
-- Name: FUNCTION similarity(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.similarity(text, text) TO rodizio_user;


--
-- Name: FUNCTION similarity_dist(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.similarity_dist(text, text) TO rodizio_user;


--
-- Name: FUNCTION similarity_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.similarity_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION strict_word_similarity(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.strict_word_similarity(text, text) TO rodizio_user;


--
-- Name: FUNCTION strict_word_similarity_commutator_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.strict_word_similarity_commutator_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION strict_word_similarity_dist_commutator_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.strict_word_similarity_dist_commutator_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION strict_word_similarity_dist_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.strict_word_similarity_dist_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION strict_word_similarity_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.strict_word_similarity_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_updated_at_column() TO rodizio_user;


--
-- Name: FUNCTION uuid_generate_v1(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1() TO rodizio_user;


--
-- Name: FUNCTION uuid_generate_v1mc(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1mc() TO rodizio_user;


--
-- Name: FUNCTION uuid_generate_v3(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v3(namespace uuid, name text) TO rodizio_user;


--
-- Name: FUNCTION uuid_generate_v4(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v4() TO rodizio_user;


--
-- Name: FUNCTION uuid_generate_v5(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v5(namespace uuid, name text) TO rodizio_user;


--
-- Name: FUNCTION uuid_nil(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_nil() TO rodizio_user;


--
-- Name: FUNCTION uuid_ns_dns(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_dns() TO rodizio_user;


--
-- Name: FUNCTION uuid_ns_oid(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_oid() TO rodizio_user;


--
-- Name: FUNCTION uuid_ns_url(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_url() TO rodizio_user;


--
-- Name: FUNCTION uuid_ns_x500(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_x500() TO rodizio_user;


--
-- Name: FUNCTION word_similarity(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.word_similarity(text, text) TO rodizio_user;


--
-- Name: FUNCTION word_similarity_commutator_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.word_similarity_commutator_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION word_similarity_dist_commutator_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.word_similarity_dist_commutator_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION word_similarity_dist_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.word_similarity_dist_op(text, text) TO rodizio_user;


--
-- Name: FUNCTION word_similarity_op(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.word_similarity_op(text, text) TO rodizio_user;


--
-- Name: TABLE comum_config; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.comum_config TO rodizio_user;


--
-- Name: TABLE comum_horarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.comum_horarios TO rodizio_user;


--
-- Name: SEQUENCE comum_horarios_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.comum_horarios_id_seq TO rodizio_user;


--
-- Name: TABLE comuns; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.comuns TO rodizio_user;


--
-- Name: TABLE escala; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.escala TO rodizio_user;


--
-- Name: SEQUENCE escala_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.escala_id_seq TO rodizio_user;


--
-- Name: TABLE escala_publicacao; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.escala_publicacao TO rodizio_user;


--
-- Name: TABLE escala_rjm; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.escala_rjm TO rodizio_user;


--
-- Name: TABLE indisponibilidades; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.indisponibilidades TO rodizio_user;


--
-- Name: SEQUENCE indisponibilidades_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.indisponibilidades_id_seq TO rodizio_user;


--
-- Name: TABLE logs_auditoria; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.logs_auditoria TO rodizio_user;


--
-- Name: TABLE organista_dias_permitidos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.organista_dias_permitidos TO rodizio_user;


--
-- Name: TABLE organista_regras_especiais; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.organista_regras_especiais TO rodizio_user;


--
-- Name: TABLE organista_tipos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.organista_tipos TO rodizio_user;


--
-- Name: TABLE organistas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.organistas TO rodizio_user;


--
-- Name: TABLE regionais; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.regionais TO rodizio_user;


--
-- Name: TABLE sub_regionais; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sub_regionais TO rodizio_user;


--
-- Name: TABLE trocas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.trocas TO rodizio_user;


--
-- Name: TABLE trocas_historico; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.trocas_historico TO rodizio_user;


--
-- Name: SEQUENCE trocas_historico_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.trocas_historico_id_seq TO rodizio_user;


--
-- Name: TABLE usuarios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.usuarios TO rodizio_user;


--
-- PostgreSQL database dump complete
--

\unrestrict pgdqByVdAuMeNuxIqey3MaNSPFef5JPdUBR0b7FdCFl0rc4WgccteLaF0CzIaDI

