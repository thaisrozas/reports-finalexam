import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import glob
import numpy as np

# Function to clean and process the data
def process_data(file_path):
    df = pd.read_csv(file_path, delimiter=',', skiprows=1)
    df.columns = df.columns.str.strip()

    # Convert percentage strings to floats
    columns_to_clean = [
        'Nota média das primeiras tentativas',
        'Nota média de todas as tentativas',
        'Média das notas das últimas tentativas',
        'Média das notas das tentativas como maior nota',
        'Nota mediana (para primeira tentativa)',
        'Desvio padrão (para primeira tentativa)'
    ]

    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).replace(',', '.').replace('%', '') if pd.notnull(x) else np.nan)
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.warning(f"Column {col} not found in the file {file_path}.")

    # Convert time intervals to hours
    def convert_to_hours(time_str):
        if isinstance(time_str, str):
            parts = time_str.split()
            days = int(parts[0]) * 24
            hours = int(parts[2])
            return days + hours
        else:
            return np.nan  # Handle non-string cases

    df['Abrir para (hours)'] = df['Abrir para'].apply(convert_to_hours)

    # Extract date from the first column
    def extract_date(date_str):
        if isinstance(date_str, str):
            try:
                return pd.to_datetime(date_str.split(',')[1].strip(), format="%d %b. %Y")
            except (IndexError, ValueError) as e:
                st.error(f"Error parsing date: {e}")
                return np.nan
        else:
            return np.nan

    df['Data'] = df['Abrir o questionário'].apply(extract_date)
    
    return df

# Step 1: Use glob to find all CSV files in the specified directory
csv_files = glob.glob('./csv/*.csv')  # Adjust the path to your directory

# Step 2: Process each CSV file and combine them into a single DataFrame
dfs = []
for file in csv_files:
    try:
        dfs.append(process_data(file))
    except Exception as e:
        st.error(f"Error processing file {file}: {e}")

df_combined = pd.concat(dfs, ignore_index=True)

# Streamlit UI

# Title
st.title('Análise de Notas do Questionário - Comparação de Vários Arquivos')

# Display the combined data (optional)
st.write('Dados Combinados dos CSVs:')
st.dataframe(df_combined)

# Step 3: Visualize the data

# Example 1: Distribution of the first attempt scores
st.subheader('Distribuição da Nota Média das Primeiras Tentativas')
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.histplot(df_combined['Nota média das primeiras tentativas'], bins=10, kde=True, ax=ax1)
ax1.set_title('Distribuição da Nota Média das Primeiras Tentativas')
ax1.set_xlabel('Nota Média (%)')
ax1.set_ylabel('Frequência')
st.pyplot(fig1)

# Example 2: Mediana - Distribution of median scores
st.subheader('Distribuição da Nota Mediana (Primeira Tentativa)')
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.histplot(df_combined['Nota mediana (para primeira tentativa)'], bins=10, kde=True, ax=ax2)
ax2.set_title('Distribuição da Nota Mediana')
ax2.set_xlabel('Nota Mediana (%)')
ax2.set_ylabel('Frequência')
st.pyplot(fig2)

# Example 3: Desvio Padrão - Distribution of standard deviation scores
st.subheader('Distribuição do Desvio Padrão (Primeira Tentativa)')
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.histplot(df_combined['Desvio padrão (para primeira tentativa)'], bins=10, kde=True, ax=ax3)
ax3.set_title('Distribuição do Desvio Padrão')
ax3.set_xlabel('Desvio Padrão (%)')
ax3.set_ylabel('Frequência')
st.pyplot(fig3)
