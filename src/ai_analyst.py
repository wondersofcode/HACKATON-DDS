def generate_business_report(hex_data, business_type):
    competitors = hex_data.get('competitor_count', 0)
    magnets = hex_data.get('magnet_count', 0)
    score = hex_data.get('score', 0)
    
    report = f"**Professional Insight for {business_type}**\n\n"
    report += f"- **Target Area Score:** {score:.1f}/10\n"
    report += f"- **Market Saturation:** Found {competitors} direct competitors.\n"
    report += f"- **Foot Traffic Drivers:** {magnets} key magnets (transit, universities, etc.) nearby.\n\n"
    
    if score >= 8:
        report += "🟢 **Recommendation:** Highly favorable location. Strong magnet presence with manageable competition. Excellent foot traffic potential."
    elif score >= 5:
        report += "🟡 **Recommendation:** Moderate potential. Requires careful marketing to beat existing competitors. Look for specific micro-location advantages."
    else:
        report += "🔴 **Recommendation:** High risk. Low foot traffic drivers or oversaturated market. Consider finding alternative hex grids."
        
    return report