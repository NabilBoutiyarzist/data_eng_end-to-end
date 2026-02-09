with source as (
      select * from read_csv(
          'data/store.csv',
          delim=';',
          header=True,
          all_varchar=True
      )
),

renamed as (
    select
        -- Clé primaire
        CAST(CMINT as VARCHAR) as id_magasin,

        -- Informations descriptives
        CAST(NOM as VARCHAR) as nom_magasin,
        CAST(NOM_COURT as VARCHAR) as nom_court_magasin,
        CAST(REGION as VARCHAR) as region,
        CAST(TYPE_SITE as VARCHAR) as type_site,
        
        -- Données numériques et Géographiques 
        CAST(SURFACE_M2 as INT) as surface_m2,
        CAST(REPLACE(Latitude, ',', '.') as DOUBLE) as latitude,
        CAST(REPLACE(Longitude, ',', '.') as DOUBLE) as longitude,
        CAST(NPA as VARCHAR) as code_postal

    from source
)

select * from renamed