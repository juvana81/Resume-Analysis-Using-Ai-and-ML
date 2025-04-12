import matplotlib.pyplot as plt
import os
import uuid

def generate_charts(user_data, prediction_proba):
    charts = {}

    # Pie Chart for Placement Chances
    fig, ax = plt.subplots()
    ax.pie([prediction_proba, 1 - prediction_proba], labels=["Placed", "Not Placed"], autopct='%1.1f%%', colors=['green', 'red'])
    pie_path = f'static/pie_{uuid.uuid4().hex}.png'
    plt.savefig(pie_path)
    charts['placement_pie'] = pie_path
    plt.close()

    # Bar Chart for Skills
    skill_scores = {k: v for k, v in user_data.items() if 'skill_' in k}
    plt.figure(figsize=(10,4))
    plt.bar(skill_scores.keys(), skill_scores.values(), color='skyblue')
    plt.xticks(rotation=45)
    plt.ylabel("Presence")
    bar_path = f'static/bar_{uuid.uuid4().hex}.png'
    plt.tight_layout()
    plt.savefig(bar_path)
    charts['skill_bar'] = bar_path
    plt.close()

    return charts
