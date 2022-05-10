from decimal import Decimal

from django.db.models import (
    Manager,
    OuterRef,
    ExpressionWrapper,
    Value,
    Sum,
    F,
    Case,
    When,
    Window,
    Q,
    Avg,
    CharField,
    BooleanField,
)
from django.db.models.functions import Cast, NullIf
from django.db.models.lookups import GreaterThan, LessThan

from core import models as cm


class PricingScenarioScopeManager(Manager):
    """
    Manager that produces an annotated queryset at the Scope level. Can be
    used by accessing `PricingScenarioScope.annotated` as opposed to
    `PricingScenarioScope.objects`.
    """

    def get_queryset(self):
        """
        Override the default queryset with additional field annotations.
        All fields are read-only, and so should not impact create/edit
        endpoints.

        @return: The original queryset, with no rows dropped, but with
        extra fields added where appropriate.
        """
        qs = super().get_queryset()

        qs = self.nbob_fields(qs)
        qs = self.national_elasticity(qs)
        qs = self.aur(qs)
        qs = self.mcp(qs)

        return qs

    @staticmethod
    def nbob_fields(qs):
        """
        Using subqueries, select the OB Role associated with the scope's article's
        opstudy. Feed this role into further subqueries to select the min and max
        NB / OB gap, and annotate all three fields at the scope level.
        """
        ob_role = cm.NBOBRole.objects.filter(opstudy=OuterRef("article__opstudy_id"))[
            :1
        ].values("ob_role")
        ob_min = cm.NBOBPair.objects.filter(ob_role=OuterRef("ob_role"))[:1].values(
            "min_percent_price_diff"
        )
        ob_max = cm.NBOBPair.objects.filter(ob_role=OuterRef("ob_role"))[:1].values(
            "max_percent_price_diff"
        )

        return qs.annotate(
            ob_role=ob_role,
            nb_ob_min_gap_pct=ob_min,
            nb_ob_max_gap_pct=ob_max,
        )

    @staticmethod
    def national_elasticity(qs):
        """
        Aggregate on related ScenarioScopeZoneDetails objects to average
        zone-level elasticity values into a national elasticity value.
        """
        return qs.annotate(national_elasticity=Avg("zone_details__elasticity"))

    @staticmethod
    def aur(qs):
        """
        AUR (average unit retail) is most easily computed / used at the zone level,
        but is stored and serialized at the scope level.  Create a subquery to pull
        the current (baseline) and suggested (pricing recommended, inclusive of
        overrides) AUR values, storing these along with absolute and percentage
        change values.
        """
        query = cm.ScenarioScopeZoneDetails.objects.filter(
            pricingscenarioscope_id=OuterRef("id")
        )[:1]

        return qs.annotate(
            curr_aur=query.values("curr_aur"),
            sugg_aur=query.values("sugg_aur"),
            aur_change=F("sugg_aur") - F("curr_aur"),
            aur_change_pct=(F("sugg_aur") - F("curr_aur")) / F("curr_aur") * 100,
        )

    @staticmethod
    def mcp(qs):
        return qs.annotate(
            curr_mcp_sur=(
                cm.PricingScenarioScope.objects.filter(pk=OuterRef("pk"))
                .filter(
                    article__current__price__isnull=False,
                    article__current__zone__store_count__isnull=False,
                )
                .values("article__current__price")
                .annotate(freq=Sum("article__current__zone__store_count"))
                .order_by("-freq")[:1]
                .values("article__current__price")
            ),
            curr_mcp_tiered_multiple=(
                cm.PricingScenarioScope.objects.filter(pk=OuterRef("pk"))
                .filter(
                    article__current__tiered_multiple__isnull=False,
                    article__current__zone__store_count__isnull=False,
                )
                .values("article__current__tiered_multiple")
                .annotate(freq=Sum("article__current__zone__store_count"))
                .order_by("-freq")[:1]
                .values("article__current__tiered_multiple")
            ),
            curr_mcp_tiered_price=(
                cm.PricingScenarioScope.objects.filter(pk=OuterRef("pk"))
                .filter(
                    article__current__tiered_price__isnull=False,
                    article__current__zone__store_count__isnull=False,
                )
                .values("article__current__tiered_price")
                .annotate(freq=Sum("article__current__zone__store_count"))
                .order_by("-freq")[:1]
                .values("article__current__tiered_price")
            ),
            planned_mcp_sur=(
                cm.ScenarioScopeZoneDetails.objects.filter(
                    pricingscenarioscope=OuterRef("pk"),
                    suggested_price__isnull=False,
                    zone__store_count__isnull=False,
                )
                .values("suggested_price")
                .annotate(freq=Sum("zone__store_count"))
                .order_by("-freq")[:1]
                .values("suggested_price")
            ),
            planned_mcp_tiered_multiple=(
                cm.ScenarioScopeZoneDetails.objects.filter(
                    pricingscenarioscope=OuterRef("pk"),
                    suggested_tiered_multiple__isnull=False,
                    zone__store_count__isnull=False,
                )
                .values("suggested_tiered_multiple")
                .annotate(freq=Sum("zone__store_count"))
                .order_by("-freq")[:1]
                .values("suggested_tiered_multiple")
            ),
            planned_mcp_tiered_price=(
                cm.ScenarioScopeZoneDetails.objects.filter(
                    pricingscenarioscope=OuterRef("pk"),
                    suggested_tiered_price__isnull=False,
                    zone__store_count__isnull=False,
                )
                .values("suggested_tiered_price")
                .annotate(freq=Sum("zone__store_count"))
                .order_by("-freq")[:1]
                .values("suggested_tiered_price")
            ),
            mcp_sur_change=F("planned_mcp_sur") - F("curr_mcp_sur"),
            mcp_sur_change_pct=(F("planned_mcp_sur") - F("curr_mcp_sur"))
            / F("curr_mcp_sur")
            * 100,
        )


class ScenarioScopeZoneDetailsManager(Manager):
    """
    Manager that produces an annotated queryset at the Scope-Zone level. Replaces the
    original manager, so should be accessed at `ScenarioScopeZoneDetails.objects`.
    """

    def get_queryset(self):
        """
        Override the default queryset with additional field annotations.
        All fields are read-only, and so should not impact create/edit
        endpoints.

        @return: The original queryset, with no rows dropped, but with
        extra fields added where appropriate.
        """
        qs = super().get_queryset()
        qs = qs.filter(
            Q(zone=F("pricingscenarioscope__recommended__zone_id"))
            & Q(zone=F("pricingscenarioscope__article__current__zone_id"))
            & Q(zone=F("pricingscenarioscope__article__costs__zone_id")),
        )

        qs = self.suggested_price(qs)
        qs = self.suggested_tiered_price(qs)
        qs = self.suggested_tiered_multiple(qs)

        qs = self.comp_incr_fields(qs)
        qs = self.aur_zone_level(qs)

        qs = self.comp_index_bpi(qs)
        qs = self.comp_index_bpi_bl(qs)
        qs = self.comp_index_api(qs)
        qs = self.comp_index_api_bl(qs)

        qs = self.get_competitor_types(qs)
        qs = self.get_competitor_ranges(qs)
        qs = self.comp_index_violations(qs)

        return qs

    @staticmethod
    def suggested_price(qs):
        """
        Compute the suggested price, inclusive of overrides.  Preferentially select the
        CM level override, or if it doesn't exist, the Pricing level override.  If this
        does not exist, select the model recommended price, which may be None.
        """
        cm_sugg = cm.PricingCMPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("price")

        pr_sugg = cm.PricingPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("price")

        sc_sugg = cm.PricingRecommendedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("price")

        return (
            qs.alias(sugg=cm_sugg)
            .alias(
                suggested=Case(When(sugg__isnull=True, then=pr_sugg), default=F("sugg"))
            )
            .annotate(
                suggested_price=Case(
                    When(suggested__isnull=True, then=sc_sugg), default=F("suggested")
                )
            )
        )

    @staticmethod
    def suggested_tiered_price(qs):
        """
        Compute the suggested price, inclusive of overrides.  Preferentially select the
        CM level override, or if it doesn't exist, the Pricing level override.  If this
        does not exist, select the model recommended price, which may be None.
        """
        cm_sugg = cm.PricingCMPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_price")

        pr_sugg = cm.PricingPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_price")

        sc_sugg = cm.PricingRecommendedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_price")

        return (
            qs.alias(sugg=cm_sugg)
            .alias(
                suggested=Case(When(sugg__isnull=True, then=pr_sugg), default=F("sugg"))
            )
            .annotate(
                suggested_tiered_price=Case(
                    When(suggested__isnull=True, then=sc_sugg), default=F("suggested")
                )
            )
        )

    @staticmethod
    def suggested_tiered_multiple(qs):
        """
        Compute the suggested price, inclusive of overrides.  Preferentially select the
        CM level override, or if it doesn't exist, the Pricing level override.  If this
        does not exist, select the model recommended price, which may be None.
        """
        cm_sugg = cm.PricingCMPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_multiple")

        pr_sugg = cm.PricingPlannedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_multiple")

        sc_sugg = cm.PricingRecommendedPrice.objects.filter(
            pricingscenarioscope_id=OuterRef("pricingscenarioscope_id"),
            zone=OuterRef("zone"),
        ).values("tiered_multiple")

        return (
            qs.alias(sugg=cm_sugg)
            .alias(
                suggested=Case(When(sugg__isnull=True, then=pr_sugg), default=F("sugg"))
            )
            .annotate(
                suggested_tiered_multiple=Case(
                    When(suggested__isnull=True, then=sc_sugg), default=F("suggested")
                )
            )
        )

    @staticmethod
    def aur_zone_level(qs):
        """
        AUR (average unit retail) is a scope-level average of suggested prices
        (inclusive of overrides) across all zones.  It is weighted by total units in
        each zone.  Though the final value lives at the scope level, it is used
        heavily in zone level calculations and so is computed at this level.

        To calculate, use a series of Window functions partitioned on scope ID.  Using
        Windows allows for the results to be computed at a partition level, but stored
        at a row level (i.e. Compute an aggregated scope-level field, but annotate
        at a scope-zone level).
        """
        return (
            qs.alias(
                s_numerator=Window(
                    expression=Sum(F("suggested_price") * F("total_units")),
                    partition_by=[F("pricingscenarioscope_id")],
                )
            )
            .alias(
                s_denominator=Window(
                    expression=Sum("total_units"),
                    partition_by=[F("pricingscenarioscope_id")],
                )
            )
            .annotate(
                sugg_aur=(
                    F("s_numerator") / NullIf(F("s_denominator"), Value(Decimal("0.0")))
                )
            )
            .alias(
                c_numerator=Window(
                    expression=Sum(
                        F("pricingscenarioscope__article__current__price")
                        * F("curr_units")
                    ),
                    partition_by=[F("pricingscenarioscope_id")],
                )
            )
            .alias(
                c_denominator=Window(
                    expression=Sum("curr_units"),
                    partition_by=[F("pricingscenarioscope_id")],
                )
            )
            .annotate(
                curr_aur=(
                    F("c_numerator") / NullIf(F("c_denominator"), Value(Decimal("0.0")))
                )
            )
        )

    @staticmethod
    def comp_index_bpi(qs):
        """
        Compare the suggested AUR to the primary and secondary competitors' prices to
        produce the Suggested BPI.
        """
        return qs.annotate(
            sugg_primary_bpi=(F("sugg_aur") / F("primary_comp_price") * 100),
            sugg_secondary_bpi=(F("sugg_aur") / F("secondary_comp_price") * 100),
        )

    @staticmethod
    def comp_index_bpi_bl(qs):
        """
        Compare the current AUR to the primary and secondary competitors' prices to
        produce the Current BPI.
        """
        return qs.annotate(
            curr_primary_bpi=(F("curr_aur") / F("primary_comp_price") * 100),
            curr_secondary_bpi=(F("curr_aur") / F("secondary_comp_price") * 100),
        )

    @staticmethod
    def comp_index_api(qs):
        """
        Compare the suggested AUR to the primary and secondary competitors' API prices,
        factoring in discount percentage, to produce the Suggested API.
        """
        return qs.annotate(
            sugg_primary_api=(
                F("sugg_aur")
                * (1 - F("discount_pct"))
                / F("primary_comp_price_api")
                * 100
            ),
            sugg_secondary_api=(
                F("sugg_aur")
                * (1 - F("discount_pct"))
                / F("secondary_comp_price_api")
                * 100
            ),
        )

    @staticmethod
    def comp_index_api_bl(qs):
        """
        Compare the current AUR to the primary and secondary competitors' API prices,
        factoring in discount percentage, to produce the Current API.
        """
        return qs.annotate(
            curr_primary_api=(
                F("curr_aur")
                * (1 - F("discount_pct"))
                / F("primary_comp_price_api")
                * 100
            ),
            curr_secondary_api=(
                F("curr_aur")
                * (1 - F("discount_pct"))
                / F("secondary_comp_price_api")
                * 100
            ),
        )

    @staticmethod
    def comp_incr_fields(qs):
        """
        Compute the difference between total profit/volume/revenue (simulated based
        on suggested price, inclusive of overrides) and current baselines.
        """
        return qs.annotate(
            incr_gp=F("total_gp") - F("curr_gp"),
            incr_units=F("total_units") - F("curr_units"),
            incr_sales=F("total_sales") - F("curr_sales"),
        )

    @staticmethod
    def get_competitor_types(qs):
        """
        Using a subquery, determine the name of the primary and secondary competitors.
        First search for a specific match by zone, and if none are found, search on
        all zones.
        """
        outer_zone = Cast(OuterRef("zone"), output_field=CharField())
        query = cm.CompetitorWeighting.objects.filter(
            opstudy=OuterRef("pricingscenarioscope__article__opstudy_id"),
        )

        return qs.alias(
            primary=query.filter(zone=outer_zone).values("primary_competitor_name"),
            secondary=query.filter(zone=outer_zone).values("secondary_competitor_name"),
        ).annotate(
            primary_competitor=Case(
                When(
                    primary__isnull=True,
                    then=query.filter(zone__iexact="all").values(
                        "primary_competitor_name"
                    ),
                ),
                default=F("primary"),
            ),
            secondary_competitor=Case(
                When(
                    secondary__isnull=True,
                    then=query.filter(zone__iexact="all").values(
                        "secondary_competitor_name"
                    ),
                ),
                default=F("secondary"),
            ),
        )

    @staticmethod
    def get_competitor_ranges(qs):
        """
        Using subqueries, determine KVI Class and Promo Status.  Then use subqueries
        to search by these fields along with opstudy and zone (either of which could
        be "all") for the primary and secondary target indices.  These are targets
        set by users.

        Because queries at any level of specificity could produce the correct targets,
        store the output of all searches except the final one as intermediate aliases
        that will not reach the final output.  At the final layer, annotate the
        queryset with the most specific possible value.
        """
        kvi_class = cm.KVIPromoStatus.objects.filter(
            article=OuterRef("pricingscenarioscope__article_id")
        ).values("kvi_class")

        promo_status = cm.KVIPromoStatus.objects.filter(
            article=OuterRef("pricingscenarioscope__article_id")
        ).values("promo_status")

        query1 = cm.PriceIndexTarget.objects.filter(
            scenario=OuterRef("pricingscenarioscope__scenario"),
            opstudy=OuterRef("pricingscenarioscope__article__opstudy_id"),
            zone=Cast(OuterRef("zone"), CharField()),
            kvi_class__iexact=OuterRef("kvi_class"),
            promo_status__iexact=OuterRef("promo_status"),
        )

        query2 = cm.KVIIndexTarget.objects.filter(
            opstudy=Cast(
                OuterRef("pricingscenarioscope__article__opstudy_id"), CharField()
            ),
            zone=Cast(OuterRef("zone"), CharField()),
            kvi_class__iexact=OuterRef("kvi_class"),
            promo_status__iexact=OuterRef("promo_status"),
        )

        query3 = cm.PriceIndexTarget.objects.filter(
            scenario=OuterRef("pricingscenarioscope__scenario"),
            opstudy=OuterRef("pricingscenarioscope__article__opstudy_id"),
            zone__iexact="all",
            kvi_class__iexact=OuterRef("kvi_class"),
            promo_status__iexact=OuterRef("promo_status"),
        )

        query4 = cm.KVIIndexTarget.objects.filter(
            opstudy=Cast(
                OuterRef("pricingscenarioscope__article__opstudy_id"), CharField()
            ),
            zone__iexact="all",
            kvi_class__iexact=OuterRef("kvi_class"),
            promo_status__iexact=OuterRef("promo_status"),
        )

        query5 = cm.KVIIndexTarget.objects.filter(
            opstudy__iexact="all",
            zone__iexact="all",
            kvi_class__iexact=OuterRef("kvi_class"),
            promo_status__iexact=OuterRef("promo_status"),
        )

        return (
            qs.alias(kvi=kvi_class, promo=promo_status)
            .alias(
                kvi_class=Case(
                    When(kvi__isnull=True, then=Value("non-kvi")),
                    default=F("kvi"),
                ),
                promo_status=Case(
                    When(promo__isnull=True, then=Value("non-promo")),
                    default=F("promo"),
                ),
            )
            .alias(
                primary_p1_from=query1.filter(
                    primary_secondary__iexact="primary",
                    competitor_type__iexact=OuterRef("primary_competitor"),
                ).values("index_min"),
                primary_p1_to=query1.filter(
                    primary_secondary__iexact="primary",
                    competitor_type__iexact=OuterRef("primary_competitor"),
                ).values("index_max"),
                secondary_p1_from=query1.filter(
                    primary_secondary__iexact="secondary",
                    competitor_type__iexact=OuterRef("secondary_competitor"),
                ).values("index_min"),
                secondary_p1_to=query1.filter(
                    primary_secondary__iexact="secondary",
                    competitor_type__iexact=OuterRef("secondary_competitor"),
                ).values("index_max"),
            )
            .alias(
                primary_p2_from=Case(
                    When(
                        primary_p1_from__isnull=True,
                        then=query2.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("primary_p1_from"),
                ),
                primary_p2_to=Case(
                    When(
                        primary_p1_to__isnull=True,
                        then=query2.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("primary_p1_to"),
                ),
                secondary_p2_from=Case(
                    When(
                        secondary_p1_from__isnull=True,
                        then=query2.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("secondary_p1_from"),
                ),
                secondary_p2_to=Case(
                    When(
                        secondary_p1_to__isnull=True,
                        then=query2.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("secondary_p1_to"),
                ),
            )
            .alias(
                primary_p3_from=Case(
                    When(
                        primary_p2_from__isnull=True,
                        then=query3.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("primary_p2_from"),
                ),
                primary_p3_to=Case(
                    When(
                        primary_p2_to__isnull=True,
                        then=query3.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("primary_p2_to"),
                ),
                secondary_p3_from=Case(
                    When(
                        secondary_p2_from__isnull=True,
                        then=query3.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("secondary_p2_from"),
                ),
                secondary_p3_to=Case(
                    When(
                        secondary_p2_to__isnull=True,
                        then=query3.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("secondary_p2_to"),
                ),
            )
            .alias(
                primary_p4_from=Case(
                    When(
                        primary_p3_from__isnull=True,
                        then=query4.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("primary_p3_from"),
                ),
                primary_p4_to=Case(
                    When(
                        primary_p3_to__isnull=True,
                        then=query4.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("primary_p3_to"),
                ),
                secondary_p4_from=Case(
                    When(
                        secondary_p3_from__isnull=True,
                        then=query4.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("secondary_p3_from"),
                ),
                secondary_p4_to=Case(
                    When(
                        secondary_p3_to__isnull=True,
                        then=query4.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("secondary_p3_to"),
                ),
            )
            .annotate(
                primary_target_bpi_min=Case(
                    When(
                        primary_p4_from__isnull=True,
                        then=query5.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("primary_p4_from"),
                ),
                primary_target_bpi_max=Case(
                    When(
                        primary_p4_to__isnull=True,
                        then=query5.filter(
                            primary_secondary__iexact="primary",
                            competitor_type__iexact=OuterRef("primary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("primary_p4_to"),
                ),
                secondary_target_bpi_min=Case(
                    When(
                        secondary_p4_from__isnull=True,
                        then=query5.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_min"),
                    ),
                    default=F("secondary_p4_from"),
                ),
                secondary_target_bpi_max=Case(
                    When(
                        secondary_p4_to__isnull=True,
                        then=query5.filter(
                            primary_secondary__iexact="secondary",
                            competitor_type__iexact=OuterRef("secondary_competitor"),
                        ).values("index_max"),
                    ),
                    default=F("secondary_p4_to"),
                ),
            )
        )

    @staticmethod
    def comp_index_violations(qs):
        """
        Compare suggsted indices (reflective of suggested prices, inclusive of
        overrides) to target indices and flag violations.  Violations occur if the
        suggested index exceeds the maximum target or falls below the minimum.
        """
        return qs.annotate(
            primary_index_violation=ExpressionWrapper(
                Q(
                    Q(
                        sugg_primary_bpi__isnull=False,
                        primary_target_bpi_max__isnull=False,
                        primary_target_bpi_min__isnull=False,
                    )
                    & (
                        GreaterThan(F("sugg_primary_bpi"), F("primary_target_bpi_max"))
                        | LessThan(F("sugg_primary_bpi"), F("primary_target_bpi_min"))
                    )
                ),
                output_field=BooleanField(),
            ),
            secondary_index_violation=ExpressionWrapper(
                Q(
                    Q(
                        sugg_secondary_bpi__isnull=False,
                        secondary_target_bpi_max__isnull=False,
                        secondary_target_bpi_min__isnull=False,
                    )
                    & (
                        GreaterThan(
                            F("sugg_secondary_bpi"), F("secondary_target_bpi_max")
                        )
                        | LessThan(
                            F("sugg_secondary_bpi"), F("secondary_target_bpi_min")
                        )
                    )
                ),
                output_field=BooleanField(),
            ),
        )
