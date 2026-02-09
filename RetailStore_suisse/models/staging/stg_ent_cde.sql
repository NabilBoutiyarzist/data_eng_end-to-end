WITH source as (
    select * from read_csv(
        'data/ent_cde.csv', 
        delim=';', 
        header=True, 
        all_varchar=True
    )
),

renamed as (
    select
        -- 1. Les Ids 
        CAST(NUMCOM as VARCHAR) as id_commande,
        CAST(CMINT as VARCHAR) as id_magasin,
        CAST(CLINUM as VARCHAR) as id_client,
        CAST(CLILIVNUM as VARCHAR) as id_client_livraison,

        -- 2. Les Dates 
        CAST(ENDSAI as DATE) as date_commande,
        TRY_CAST(LIVDAY as DATE) as date_livraison,

        -- 3. Les attributs de commande 
        CAST(TYPEDEVIS as VARCHAR) as code_canal,      -- 0 ou 54
        CAST(ENTYPE as VARCHAR) as code_type_commande, -- BL, EI...
        CAST(CNUFTRP as VARCHAR) as code_transporteur

    from source
)

select * from renamed