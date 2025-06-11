import os
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Pro variant for more comprehensive analysis
model = genai.GenerativeModel("models/gemini-1.5-pro")

def get_competitor_analysis(brand_name, website_url, include_national=True, include_regional=True, include_upcoming=True, reprompt=""):
    """
    Analyze a brand and its competitors using Gemini AI.
    
    Args:
        brand_name: Name of the brand to analyze
        website_url: URL of the brand's website
        include_national: Whether to include national competitors
        include_regional: Whether to include regional competitors
        include_upcoming: Whether to include upcoming competitors
        reprompt: Additional instructions or requests for the analysis
        
    Returns:
        Dictionary containing brand analysis and competitor information
    """
    # First, analyze the brand itself
    brand_analysis = analyze_brand(brand_name, website_url, reprompt)
    
    # Then, identify and analyze competitors
    competitors = identify_competitors(
        brand_name, 
        website_url, 
        brand_analysis["industry"],
        include_national,
        include_regional,
        include_upcoming,
        reprompt
    )
    
    # Generate recommendations and strategies
    recommendations = generate_recommendations(brand_name, brand_analysis, competitors, reprompt)
    brand_analysis["recommendations"] = recommendations
    
    # Combine the results
    return {
        "brand": brand_analysis,
        "competitors": competitors
    }

def analyze_brand(brand_name, website_url, reprompt=""):
    """
    Analyze a single brand using Gemini AI.
    
    Args:
        brand_name: Name of the brand to analyze
        website_url: URL of the brand's website
        reprompt: Additional instructions or requests for the analysis
        
    Returns:
        Dictionary containing brand analysis
    """
    prompt = f"""
    You are a market research expert. Provide a comprehensive and detailed analysis of the following brand:
    
    Brand Name: {brand_name}
    Website: {website_url}
    
    Please include:
    1. A detailed overview of what the brand does (products/services)
    2. Their target audience (be specific about demographics, psychographics, and behaviors)
    3. Their unique selling proposition and value proposition
    4. Their brand positioning and market positioning
    5. Their key products or services with detailed descriptions
    6. Their marketing strategies and channels
    7. Their brand voice and messaging
    8. The specific industry they operate in (be very specific, e.g., 'Ayurvedic medicine', not just 'healthcare')
    
    Format your response as detailed bullet points under each section.
    
    At the very end, on a separate line, provide a one-line summary of their primary industry in this format: "INDUSTRY: [specific industry name]"
    """
    
    # Add reprompt instructions if provided
    if reprompt:
        prompt += f"""
        
        ADDITIONAL INSTRUCTIONS: Please address the following specific requests in your analysis:
        {reprompt}
        """
    
    try:
        response = model.generate_content(prompt)
        analysis_text = response.text.strip()
        
        # Extract industry from the response
        industry = "Unknown"
        for line in analysis_text.split("\n"):
            if line.startswith("INDUSTRY:"):
                industry = line.replace("INDUSTRY:", "").strip()
                # Remove this line from the analysis text
                analysis_text = analysis_text.replace(line, "").strip()
                break
        
        # If no explicit industry line was found, try to infer it
        if industry == "Unknown":
            industry_prompt = f"""
            Based on this analysis of {brand_name}:
            
            {analysis_text}
            
            What specific industry does this brand operate in? Be very specific (e.g., 'Ayurvedic medicine', not just 'healthcare').
            Provide only the industry name, nothing else.
            """
            
            try:
                industry_response = model.generate_content(industry_prompt)
                industry = industry_response.text.strip()
            except Exception as e:
                industry = "Unknown"
    except Exception as e:
        analysis_text = f"Analysis not available: {e}"
        industry = "Unknown"
    
    return {
        "name": brand_name,
        "website": website_url,
        "analysis": analysis_text,
        "industry": industry
    }

def identify_competitors(brand_name, website_url, industry, include_national=True, include_regional=True, include_upcoming=True, reprompt=""):
    """
    Identify and analyze competitors of a brand using Gemini AI.
    
    Args:
        brand_name: Name of the brand to analyze
        website_url: URL of the brand's website
        industry: The specific industry the brand operates in
        include_national: Whether to include national competitors
        include_regional: Whether to include regional competitors
        include_upcoming: Whether to include upcoming competitors
        reprompt: Additional instructions or requests for the analysis
        
    Returns:
        List of dictionaries containing competitor information
    """
    # First, identify competitors
    identify_prompt = f"""
    You are a competitive intelligence expert specializing in the {industry} industry. 
    
    For the brand {brand_name} (website: {website_url}) which operates in the {industry} industry,
    identify the following competitors who are SPECIFICALLY in the SAME {industry} industry:
    """
    
    # Add competitor types based on user selection
    competitor_types = []
    if include_national:
        competitor_types.append("1. Top 3 national competitors (major players in the same {industry} market)")
    if include_regional:
        competitor_types.append("2. Top 3 regional competitors (smaller but significant {industry} brands in specific regions)")
    if include_upcoming:
        competitor_types.append("3. Top 2 upcoming competitors (emerging {industry} brands that are gaining traction)")
    
    # If no competitor types are selected, default to all
    if not competitor_types:
        competitor_types = [
            "1. Top 3 national competitors (major players in the same {industry} market)",
            "2. Top 3 regional competitors (smaller but significant {industry} brands in specific regions)",
            "3. Top 2 upcoming competitors (emerging {industry} brands that are gaining traction)"
        ]
    
    # Add competitor types to prompt
    identify_prompt += "\n\n" + "\n".join(competitor_types)
    
    identify_prompt += f"""
    
    IMPORTANT: ALL competitors MUST be in the EXACT SAME {industry} industry as {brand_name}. 
    Do NOT include brands from different industries or product categories.
    
    For each competitor, provide:
    - Name
    - Website (make an educated guess if you don't know the exact URL)
    - Category (national, regional, or upcoming)
    - Brief description of their {industry} products/services
    - Their market share or position (if known)
    - Their key strengths and weaknesses
    
    Format as a detailed list with clear sections for each category.
    """
    
    # Add reprompt instructions if provided
    if reprompt:
        identify_prompt += f"""
        
        ADDITIONAL INSTRUCTIONS: Please address the following specific requests in your competitor identification:
        {reprompt}
        """
    
    try:
        identify_response = model.generate_content(identify_prompt)
        competitors_text = identify_response.text.strip()
    except Exception as e:
        return [{"error": f"Could not identify competitors: {e}"}]
    
    # Now analyze each competitor
    analysis_prompt = f"""
    Based on the following list of competitors for {brand_name} in the {industry} industry:
    
    {competitors_text}
    
    Provide a comprehensive and detailed analysis of each competitor listed above. For each one, include:
    
    1. What they do well (strengths) in the {industry} industry
    2. Their weaknesses or areas for improvement
    3. Their flagship {industry} products or services with detailed descriptions
    4. Their pricing strategies (if known)
    5. Their marketing campaigns, strategies, and channels
    6. Their target audience and how it overlaps with {brand_name}'s audience
    7. Their unique selling propositions and value propositions
    8. Their market positioning and brand voice
    9. How they compare to {brand_name} in the {industry} market
    10. Potential threats they pose to {brand_name}
    11. Opportunities for {brand_name} to differentiate from them
    
    Format your response as a structured analysis for each competitor with clear headings and detailed bullet points.
    """
    
    # Add reprompt instructions if provided
    if reprompt:
        analysis_prompt += f"""
        
        ADDITIONAL INSTRUCTIONS: Please address the following specific requests in your competitor analysis:
        {reprompt}
        """
    
    try:
        analysis_response = model.generate_content(analysis_prompt)
        analysis_text = analysis_response.text.strip()
    except Exception as e:
        analysis_text = f"Competitor analysis not available: {e}"
    
    # Combine the results
    return {
        "identification": competitors_text,
        "analysis": analysis_text
    }

def generate_recommendations(brand_name, brand_analysis, competitors_data, reprompt=""):
    """
    Generate strategic recommendations for the brand based on the analysis.
    
    Args:
        brand_name: Name of the brand
        brand_analysis: Dictionary containing brand analysis
        competitors_data: Dictionary containing competitor information
        reprompt: Additional instructions or requests for the recommendations
        
    Returns:
        String containing recommendations and strategies
    """
    industry = brand_analysis.get("industry", "Unknown")
    
    recommendations_prompt = f"""
    You are a strategic marketing consultant specializing in the {industry} industry.
    
    Based on the following information about {brand_name} and its competitors:
    
    BRAND ANALYSIS:
    {brand_analysis['analysis']}
    
    COMPETITOR IDENTIFICATION:
    {competitors_data['identification']}
    
    COMPETITOR ANALYSIS:
    {competitors_data['analysis']}
    
    Provide comprehensive strategic recommendations for {brand_name} to improve their market position and outperform competitors. Include:
    
    1. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
    2. Detailed Marketing Strategy Recommendations
       - Digital marketing tactics
       - Content strategy
       - Social media approach
       - SEO recommendations
       - Paid advertising suggestions
    3. Product/Service Development Opportunities
    4. Pricing Strategy Recommendations
    5. Distribution Channel Optimization
    6. Brand Positioning Refinement
    7. Competitive Advantage Enhancement
    8. Target Audience Expansion Strategies
    9. Customer Retention Tactics
    10. Growth Opportunities and Timeline
    
    Format your response with clear headings and detailed bullet points for each section. Be specific, actionable, and strategic.
    """
    
    # Add reprompt instructions if provided
    if reprompt:
        recommendations_prompt += f"""
        
        ADDITIONAL INSTRUCTIONS: Please address the following specific requests in your recommendations:
        {reprompt}
        """
    
    try:
        recommendations_response = model.generate_content(recommendations_prompt)
        recommendations_text = recommendations_response.text.strip()
    except Exception as e:
        recommendations_text = f"Recommendations not available: {e}"
    
    return recommendations_text


def format_for_export(analysis_data):
    """
    Format the analysis data for export to Google Sheets.
    
    Args:
        analysis_data: Dictionary containing brand and competitor analysis
        
    Returns:
        List of dictionaries formatted for export
    """
    export_data = []
    
    # Add brand information
    export_data.append({
        "section": "Brand Analysis",
        "name": analysis_data["brand"]["name"],
        "website": analysis_data["brand"]["website"],
        "details": analysis_data["brand"]["analysis"],
        "type": f"Main Brand - {analysis_data['brand'].get('industry', 'Unknown Industry')}"
    })
    
    # Add brand recommendations if available
    if "recommendations" in analysis_data["brand"]:
        export_data.append({
            "section": "Brand Recommendations & Strategies",
            "name": analysis_data["brand"]["name"],
            "website": analysis_data["brand"]["website"],
            "details": analysis_data["brand"]["recommendations"],
            "type": "Recommendations"
        })
    
    # Add competitor identification
    export_data.append({
        "section": "Competitor Identification",
        "name": "",
        "website": "",
        "details": analysis_data["competitors"]["identification"],
        "type": "Identification"
    })
    
    # Add competitor analysis
    export_data.append({
        "section": "Competitor Analysis",
        "name": "",
        "website": "",
        "details": analysis_data["competitors"]["analysis"],
        "type": "Analysis"
    })
    
    return export_data