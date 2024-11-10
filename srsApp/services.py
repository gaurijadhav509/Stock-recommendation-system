from .models import EXCHANGE_REGION_MAP
import json
import google.generativeai as genai

def validate_exchange_region(preferred_exchange, preferred_region):
    """Validate that the preferred exchange matches the preferred region."""
    exchange_region = EXCHANGE_REGION_MAP.get(preferred_exchange)
    if not exchange_region:
        return f"Exchange '{preferred_exchange}' is not recognized."
    
    if preferred_region.lower() != exchange_region.lower():
        return f"The exchange '{preferred_exchange}' is not located in the preferred region '{preferred_region}'."
    
    return None


def get_recommendations_from_gemini(investment_preference):
    """Fetch stock recommendations from the Gemini API."""
    prompt = f"""
    Generate a JSON response of the top 5 historical stocks for last year based on the following investment preferences:
    - Risk Tolerance: {investment_preference.risk_tolerance}
    - Asset Type: {investment_preference.asset_type}
    - Preferred Region: {investment_preference.preferred_region}
    - Preferred Exchange: {investment_preference.preferred_exchange}

    Each stock should have the following fields:
    - "symbol": string
    - "company": string
    - "sector": string
    - "market_cap": number in billions
    """

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    try:
        response = model.generate_content(prompt)
        response_text = response.text
        start_index = response_text.find('[')
        end_index = response_text.rfind(']') + 1
        clean_json_str = response_text[start_index:end_index]

        if not clean_json_str:
            raise ValueError("Empty response from Gemini.")

        recommendations = json.loads(clean_json_str)
        return recommendations

    except Exception as e:
        raise ValueError(f"Error in fetching recommendations from Gemini: {str(e)}")