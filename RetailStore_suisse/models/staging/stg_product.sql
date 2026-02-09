with source as (
      select * from read_csv(
          'data/product.csv',
          delim=';',
          header=True,
          all_varchar=True
      )
),

renamed as (
    select
        -- Identifiants
        CAST(CODE_PRODUIT as VARCHAR) as code_produit, 
        CAST(EAN as VARCHAR) as code_ean,

        -- Hiérarchie / Classification
        CAST(SEGMENTATION_NEW as VARCHAR) as famille_produit,
        CAST(GROUPE_DE_CARACTERISTIQUES as VARCHAR) as groupe_caracteristique,
        CAST(LIBELLE_GROUPE_NEW as VARCHAR) as libelle_groupe,

        -- Description
        CAST(NOM_FR as VARCHAR) as nom_produit_fr,
        CAST(NOM_DE as VARCHAR) as nom_produit_de,
        CAST(NOM_IT as VARCHAR) as nom_produit_it

    from source
)

select * from renamed