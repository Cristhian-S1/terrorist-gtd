-- Base de datos principal 
select * from gtd

-- Left
select * from dim_ataque;
select * from dim_detalle;
select * from dim_tiempo;
select * from dim_lugar;
select * from dim_espec_lugar;

-- Mother center
select * from fact_gtd_event;

-- Right
select * from dim_arma;
select * from dim_objetivos;

select * from dim_gperp;
select * from dim_bt_grupo;
select * from dim_mcr;
select * from dim_perpetradores;

select * from dim_impacto;
select * from dim_detalles_a;


