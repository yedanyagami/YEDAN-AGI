import csv
import json
from datetime import datetime

# Raw data collected from Browser Subagent
raw_data = [
  {"title": "Integrating Shipping API with shopify store", "url": "https://www.reddit.com/r/shopify/comments/1n51dsz/integrating_shipping_api_with_shopify_store/", "snippet": ""},
  {"title": "USPS Contract, how to integrate APIs?", "url": "https://www.reddit.com/r/shopify/comments/1lxdqv1/usps_contract_how_to_integrate_apis/", "snippet": ""},
  {"title": "I own a shopify shop If I let my friend who is a dev make some simple integration with Shopify GraphQL API, can I still use it after 2-3 years?", "url": "https://www.reddit.com/r/shopify/comments/1n1hcqt/i_own_a_shopify_shop_if_i_let_my_friend_who_is_a/", "snippet": ""},
  {"title": "ERP for Shopify", "url": "https://www.reddit.com/r/shopify/comments/1ijo72p/erp_for_shopify/", "snippet": ""},
  {"title": "Need warehouse/inventory management solution help!", "url": "https://www.reddit.com/r/shopify/comments/1fsz9uk/need_warehouseinventory_management_solution_help/", "snippet": ""},
  {"title": "Billing API integration", "url": "https://www.reddit.com/r/shopify/comments/1b4mn7y/billing_api_integration/", "snippet": ""},
  {"title": "3rd Party API Set Up", "url": "https://www.reddit.com/r/shopify/comments/1ir28or/3rd_party_api_set_up/", "snippet": ""},
  {"title": "REST Admin API deprecation and GraphQL", "url": "https://www.reddit.com/r/shopify/comments/1g2thxv/rest_admin_api_deprecation_and_graphql/", "snippet": ""},
  {"title": "Best Shopify Shipping App / Integration?", "url": "https://www.reddit.com/r/shopify/comments/1or41oi/best_shopify_shipping_app_integration/", "snippet": ""},
  {"title": "Does integration with Wolt API require Shopify plus", "url": "https://www.reddit.com/r/shopify/comments/1j37vki/does_integration_with_wolt_api_require_shopify/", "snippet": ""},
  {"title": "REST API Deprecation [repost]", "url": "https://www.reddit.com/r/shopify/comments/1hwp21t/rest_api_deprecation_repost/", "snippet": ""},
  {"title": "Customer Privacy API not working? I keep getting undefined", "url": "https://www.reddit.com/r/shopify/comments/1ewqew5/customer_privacy_api_not_working_i_keep_getting/", "snippet": ""},
  {"title": "Need advice regarding API and manual CSV. New site", "url": "https://www.reddit.com/r/shopify/comments/1ohrszd/need_advice_regarding_api_and_manual_csv_new_site/", "snippet": ""},
  {"title": "Anyone with extensive api experience can share some best practises / lessons learned from building catalog integrations?", "url": "https://www.reddit.com/r/shopify/comments/amog20/anyone_with_extensive_api_experience_can_share/", "snippet": ""},
  {"title": "Help with 3rd Party API Fulfillment Integration Honeysplace", "url": "https://www.reddit.com/r/shopify/comments/secdd1/help_with_3rd_party_api_fulfillment_integration/", "snippet": ""},
  {"title": "Help required related to Functions Api graphql query complexity limitation.", "url": "https://www.reddit.com/r/shopify/comments/1lgvj28/help_required_related_to_functions_api_graphql/", "snippet": ""},
  {"title": "How to integrate with an API?", "url": "https://www.reddit.com/r/shopify/comments/125bdlf/how_to_integrate_with_an_api/", "snippet": ""},
  {"title": "How to integrate APIs onto Shopify website as a function?", "url": "https://www.reddit.com/r/shopify/comments/1jp0w4j/how_to_integrate_apis_onto_shopify_website_as_a/", "snippet": ""},
  {"title": "Shopify API Integration", "url": "https://www.reddit.com/r/shopify/comments/qffpmq/shopify_api_integration/", "snippet": ""},
  {"title": "How to integrate third party api to my shopify website?", "url": "https://www.reddit.com/r/shopify/comments/zm3cv5/how_to_integrate_third_party_api_to_my_shopify/", "snippet": ""},
  {"title": "What are some biggest pain points of Shopify merchants", "url": "https://www.reddit.com/r/shopify/comments/r72sp2/what_are_some_biggest_pain_points_of_shopify/", "snippet": ""},
  {"title": "Shopify API rate limits / difficulty / use cases", "url": "https://www.reddit.com/r/shopify/comments/17x2dwp/shopify_api_rate_limits_difficulty_use_cases/", "snippet": ""},
  {"title": "Etsy Integrations - Did they really block sharing shipping info API?", "url": "https://www.reddit.com/r/shopify/comments/1i7d8uh/etsy_integrations_did_they_really_block_sharing/",
  "snippet": ""},
  {"title": "Shopify Devs - How much to charge / how long to integrate personalized API data into the frontend (using Hydrogen, maybe)?", "url": "https://www.reddit.com/r/shopify/comments/1cfl1kh/shopify_devs_how_much_to_charge_how_long_to/", "snippet": ""},
  {"title": "Apple pay with authorize.net", "url": "https://www.reddit.com/r/shopify/comments/tkr8th/apple_pay_with_authorizenet/", "snippet": ""},
  {"title": "Seeking Recommendations: Best Shipping Status API", "url": "https://www.reddit.com/r/shopify/comments/1g8ujgn/seeking_recommendations_best_shipping_status_api/", "snippet": ""},
  {"title": "API to connect partner shop to marketplace", "url": "https://www.reddit.com/r/shopify/comments/sdw15q/api_to_connect_partner_shop_to_marketplace/", "snippet": ""},
  {"title": "Considering Shopify but with a question about data feeds", "url": "https://www.reddit.com/r/shopify/comments/1kwxojj/considering_shopify_but_with_a_question_about/", "snippet": ""},
  {"title": "Shopify Plus ACH Support", "url": "https://www.reddit.com/r/shopify/comments/1nkbhvl/shopify_plus_ach_support/", "snippet": ""},
  {"title": "Still not possible to search by SKU via API?", "url": "https://www.reddit.com/r/shopify/comments/691le8/still_not_possible_to_search_by_sku_via_api/", "snippet": ""},
  {"title": "Can Shopify API/app integration handle new product purchases?", "url": "https://www.reddit.com/r/shopify/comments/165hawt/can_shopify_apiapp_integration_handle_new_product/", "snippet": ""},
  {"title": "Integration template for connecting to Shopify's REST API", "url": "https://www.reddit.com/r/shopify/comments/sdto6y/integration_template_for_connecting_to_shopifys/", "snippet": ""},
  {"title": "Pre-built connector functions to integrate with the Shopify REST API.", "url": "https://www.reddit.com/r/shopify/comments/pygcf9/prebuilt_connector_functions_to_integrate_with/", "snippet": ""},
  {"title": "Best ERPs?", "url": "https://www.reddit.com/r/shopify/comments/13thzk1/best_erps/", "snippet": ""},
  {"title": "Has anyone integrated Shopify with East Coast Options via API?", "url": "https://www.reddit.com/r/shopify/comments/y13ms4/has_anyone_integrated_shopify_with_east_coast/", "snippet": ""},
  {"title": "520 error resepon, 60s default timeouts and sometimes random 50Xs", "url": "https://www.reddit.com/r/shopify/comments/x0mjv7/520_error_resepon_60s_default_timeouts_and/", "snippet": ""},
  {"title": "[GUIDE] Shopify REST API Integration", "url": "https://www.reddit.com/r/shopify/comments/mgg148/guide_shopify_rest_api_integration/", "snippet": ""},
  {"title": "How I embedded a React App inside my Shopify Storefront", "url": "https://www.reddit.com/r/shopify/comments/n0b5e8/how_i_embedded_a_react_app_inside_my_shopify/", "snippet": ""},
  {"title": "Question: where to integrate the suppliers public API", "url": "https://www.reddit.com/r/shopify/comments/njv836/question_where_to_integrate_the_suppliers_public/", "snippet": ""},
  {"title": "Need help integrating Wave with Shopify, how are you doing it?", "url": "https://www.reddit.com/r/shopify/comments/dd9mac/need_help_integrating_wave_with_shopify_how_are/", "snippet": ""},
  {"title": "With shopify what level of access do you have to the code and database?", "url": "https://www.reddit.com/r/shopify/comments/1h0l4kz/with_shopify_what_level_of_access_do_you_have_to/", "snippet": ""},
  {"title": "App Dev - Rest API Call Help", "url": "https://www.reddit.com/r/shopify/comments/ia5k40/app_dev_rest_api_call_help/", "snippet": ""},
  {"title": "Cart abandonment - I’m getting fed up.", "url": "https://www.reddit.com/r/shopify/comments/1k96mol/cart_abandonment_im_getting_fed_up/", "snippet": ""},
  {"title": "Has anyone had a bug on their business manager? 10.200$ lost in the last 2 weeks", "url": "https://www.reddit.com/r/shopify/comments/pkhpxu/has_anyone_had_a_bug_on_their_business_manager/", "snippet": ""},
  {"title": "Integrating with a custom API out side of Shopify to log in a VIP customer", "url": "https://www.reddit.com/r/shopify/comments/nivpqv/integrating_with_a_custom_api_out_side_of_shopify/", "snippet": ""},
  {"title": "Building a Node app with Typescript", "url": "https://www.reddit.com/r/shopify/comments/hu3953/building_a_node_app_with_typescript/", "snippet": ""},
  {"title": "Canada Post & Zonos Partnership", "url": "https://www.reddit.com/r/shopify/comments/1my7455/canada_post_zonos_partnership/", "snippet": ""},
  {"title": "Setting up Shipping infrastructure for ecommerce", "url": "https://www.reddit.com/r/shopify/comments/v1xz04/setting_up_shipping_infrastructure_for_ecommerce/", "snippet": ""},
  {"title": "How to fully integrate shopify store into my own website?", "url": "https://www.reddit.com/r/shopify/comments/i4ca64/how_to_fully_integrate_shopify_store_into_my_own/", "snippet": ""},
  {"title": "Looking for order processing software with Shopify integration.", "url": "https://www.reddit.com/r/shopify/comments/5lz1r9/looking_for_order_processing_software_with/", "snippet": ""},
  {"title": "How do you prevent inventory sync disasters during peak season?", "url": "https://www.reddit.com/r/shopify/comments/1n9oplg/how_do_you_prevent_inventory_sync_disasters/", "snippet": ""},
  {"title": "Ayone have success using syncee app, whats your experience, im located in canada isit good for my region", "url": "https://www.reddit.com/r/shopify/comments/1kr5hl5/ayone_have_success_using_syncee_app_whats_your/", "snippet": ""},
  {"title": "Shopify Cross Platform Help", "url": "https://www.reddit.com/r/shopify/comments/1lmaee6/shopify_cross_platform_help/", "snippet": ""},
  {"title": "Selling cross platform", "url": "https://www.reddit.com/r/shopify/comments/1cpa0bs/selling_cross_platform/", "snippet": ""},
  {"title": "Shopify app that can do real-time metafield sync between two shopify stores?", "url": "https://www.reddit.com/r/shopify/comments/1l8fm3u/shopify_app_that_can_do_realtime_metafield_sync/", "snippet": ""},
  {"title": "Connection Issue Need Advice!", "url": "https://www.reddit.com/r/shopify/comments/1m0wltt/connection_issue_need_advice/", "snippet": ""},
  {"title": "Platform for B2B Ordering, Faire Sync or Shopify App?", "url": "https://www.reddit.com/r/shopify/comments/1kijqih/platform_for_b2b_ordering_faire_sync_or_shopify/", "snippet": ""},
  {"title": "Syncing between two Shopify stores (i.e D2C and Wholesale)", "url": "https://www.reddit.com/r/shopify/comments/1jjvrd0/syncing_between_two_shopify_stores_ie_d2c_and/", "snippet": ""},
  {"title": "Multiple currencies, markets, and google merchant center. Has anyone managed to make them play nicely together?", "url": "https://www.reddit.com/r/shopify/comments/1kea2q3/multiple_currencies_markets_and_google_merchant/", "snippet": ""},
  {"title": "Hubspot vs Klaviyo and connecting metafields", "url": "https://www.reddit.com/r/shopify/comments/1iikjp5/hubspot_vs_klaviyo_and_connecting_metafields/", "snippet": ""},
  {"title": "Problems with AutoSync Shopify/Square app", "url": "https://www.reddit.com/r/shopify/comments/18d1gad/problems_with_autosync_shopifysquare_app/", "snippet": ""},
  {"title": "SHOPIFY POS Go - Won’t connect", "url": "https://www.reddit.com/r/shopify/comments/17l3erf/shopify_pos_go_wont_connect/", "snippet": ""},
  {"title": "Need an app which could sync products between store and also has price transformation", "url": "https://www.reddit.com/r/shopify/comments/1ktzkhg/need_an_app_which_could_sync_products_between/", "snippet": ""},
  {"title": "What tools are you using to sync inventory and orders between multiple shops like shopify and etsy or amazon?", "url": "https://www.reddit.com/r/shopify/comments/lcoqjc/what_tools_are_you_using_to_sync_inventory_and/", "snippet": ""},
  {"title": "Potential Issues with adding a Shopify Collective customer added to B2B company?", "url": "https://www.reddit.com/r/shopify/comments/1j2m03l/potential_issues_with_adding_a_shopify_collective/", "snippet": ""},
  {"title": "Is my store dead?", "url": "https://www.reddit.com/r/shopify/comments/1o8snq3/is_my_store_dead/", "snippet": ""},
  {"title": "Looking for a solution to managing the same products/inventory across multiple stores", "url": "https://www.reddit.com/r/shopify/comments/1ezhffm/looking_for_a_solution_to_managing_the_same/", "snippet": ""},
  {"title": "Help Integrating Reviews from Multiple Platforms and Displaying Them Prominently", "url": "https://www.reddit.com/r/shopify/comments/1axikvs/help_integrating_reviews_from_multiple_platforms/", "snippet": ""},
  {"title": "Can't connect CNAME on third party domain website", "url": "https://www.reddit.com/r/shopify/comments/1aisyz4/cant_connect_cname_on_third_party_domain_website/", "snippet": ""},
  {"title": "Best way to sync Etsy listings with Shopify?", "url": "https://www.reddit.com/r/shopify/comments/18gpn8d/best_way_to_sync_etsy_listings_with_shopify/", "snippet": ""},
  {"title": "Is Matrixify not fit for purpose? Migrating BigCommerce with custom fields to Shopify", "url": "https://www.reddit.com/r/shopify/comments/1g18pvs/is_matrixify_not_fit_for_purpose_migrating/", "snippet": ""},
  {"title": "How to get my Shopify to sync", "url": "https://www.reddit.com/r/shopify/comments/178usmp/how_to_get_my_shopify_to_sync/", "snippet": ""},
  {"title": "What platform will work for me since Shopify Has Failed Me?", "url": "https://www.reddit.com/r/shopify/comments/xkmjij/what_platform_will_work_for_me_since_shopify_has/", "snippet": ""},
  {"title": "Multi-channel SKU syncing", "url": "https://www.reddit.com/r/shopify/comments/1ffphli/multichannel_sku_syncing/", "snippet": ""},
  {"title": "Shipping rates with third-party apps", "url": "https://www.reddit.com/r/shopify/comments/1hevj2o/shipping_rates_with_thirdparty_apps/", "snippet": ""}
]

def analyze_pain(title):
    title = title.lower()
    
    # Categorize
    category = "General"
    if any(x in title for x in ["sync", "inventory", "stock", "sku", "multi-channel", "cross platform"]):
        category = "Inventory/Sync"
    elif any(x in title for x in ["api", "graphql", "rest", "webhook", "function", "dev", "integrate"]):
        category = "API/Dev"
    elif any(x in title for x in ["shipping", "order", "fulfillment", "rate"]):
        category = "Shipping/Order"
    elif any(x in title for x in ["billing", "pay", "money", "lost"]):
        category = "Financial"
        
    # Sentiment/Urgency Score (1-10)
    score = 3
    if any(x in title for x in ["help", "advice", "question", "how to"]):
        score += 2
    if any(x in title for x in ["fail", "error", "bug", "issue", "problem", "broken", "undefined"]):
        score += 3
    if any(x in title for x in ["disaster", "nightmare", "dead", "fed up", "lost", "critical"]):
        score += 4
        
    return category, score

# Generate CSV
output_file = "L2_intel_stream.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Source", "Title", "Pain_Category", "Sentiment_Score", "URL"])
    
    for item in raw_data:
        cat, score = analyze_pain(item["title"])
        writer.writerow([
            datetime.now().isoformat(),
            "Reddit (r/shopify)",
            item["title"],
            cat,
            score,
            item["url"]
        ])

print(f"Successfully processed {len(raw_data)} items to {output_file}")
