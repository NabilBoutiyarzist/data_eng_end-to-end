with details as (
    select * from {{ ref('stg_det_cde') }}
),

headers as (
    select * from {{ ref('stg_ent_cde') }}
),

joined as (
    select
        -- Clés de jointure
        d.id_commande,
        d.id_magasin,
        d.num_ligne,

        -- Infos Temporelles & Dimensionnelles (Venant de l'En-tête)
        h.date_commande,
        h.date_livraison,
        h.code_canal,
        h.code_type_commande,
        h.id_client,
        h.code_transporteur,

        -- Infos Produit & Métriques (Venant du Détail)
        d.code_produit,
        d.code_produit_interne, -- Ton renommage
        d.quantite_commandee,
        d.montant_total_ligne,  -- Ce sera notre CA TTC
        d.montant_tva,
        d.prix_unitaire_vente,
        d.code_statut_ligne

    from details d
    inner join headers h
        on d.id_commande = h.id_commande
        and d.id_magasin = h.id_magasin
)

select * from joined