import pandas as pd
import plotly.express as px

def generate_treemap(data):
    # Create a treemap
    fig = px.treemap(data, path=['Taxonomic Group'], values='Count', title='Treemap of Taxonomic Groups',
                     color='Count',  # Color by Count
                     color_continuous_scale='Viridis')  # Color scale

    # Update layout to adjust text sizes
    fig.update_layout(
        title_text='Treemap of Taxonomic Groups',
        title_font_size=24,  # Title font size
        font=dict(size=18),  # Font size for labels
    )
    
    # Show the plot
    fig.write_html("treemap.html")

def main():
    # Read data from CSV file
    data = pd.read_csv('pelorus.csv')
    
    # Generate treemap
    generate_treemap(data)

if __name__ == "__main__":
    main()
