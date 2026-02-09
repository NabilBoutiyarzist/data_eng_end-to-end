with source as (
      select * from read_csv(
          'data/det_cde.csv',
          delim=';',
          header=True,
          all_varchar=True
      )
),

renamed as (
    select
      
        CAST(CMINT as VARCHAR) as id_magasin,
        CAST(NUMCOM as VARCHAR) as id_commande,
        CAST(NUMLIG as INT) as num_ligne,
        CAST(ART_EAN as VARCHAR) as code_produit,
        CAST(ARTCAINT as VARCHAR) as code_produit_interne,
        CAST(ARTLIBC as VARCHAR) as libelle_produit,

   
        CAST(ETAT as INT) as code_statut_ligne, -- 7 ou 17
        CAST(CODEREM as VARCHAR) as flag_remise,
        CAST(MOTIFREM as VARCHAR) as motif_remise,
        CAST(VENQTE as INT) as quantite_commandee,

    
        CAST(REPLACE(PRIXORI, ',', '.') AS DOUBLE) as prix_unitaire_originel,
        CAST(REPLACE(PRIXUPV, ',', '.') AS DOUBLE) as prix_unitaire_vente,
        CAST(REPLACE(MNTTOT2, ',', '.') AS DOUBLE) as montant_total_ligne,
        CAST(REPLACE(MNTTVA, ',', '.') AS DOUBLE) as montant_tva,
 
        CAST(REPLACE(REMISE, ',', '.') AS DOUBLE) as taux_remise,
        CAST(REPLACE(REMISE_POURCENT_MNT_U, ',', '.') AS DOUBLE) as montant_remise_unitaire,
        CAST(REPLACE(REMISE_EXCEPTIONNELLE__MNT_U, ',', '.') AS DOUBLE) as montant_remise_exceptionnelle

    from source
)

select * from renamed