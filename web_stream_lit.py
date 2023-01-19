import pandas as pd
import streamlit as st
from collections import Counter

def resolutor(df_datos_contados, df_visualizado, selected_dic):

    df_visualizado['Color'] = df_visualizado['Categorias'].map(selected_dic)

    df_merged_data = pd.merge(df_visualizado,df_datos_contados,on = 'Text',how= 'left')

    del df_merged_data['Categorias']

    df_merged_data['Color'],df_merged_data['Size'] = df_merged_data['Size'],df_merged_data['Color']

    df_merged_data.head()

    return df_merged_data

def ver_descarte(df_datos_contados,df_visualizado,df_palabras_a_sacar):
    df_sin_compartidos = pd.concat([df_visualizado,df_datos_contados])

    df_sin_compartidos = df_sin_compartidos.drop_duplicates(['Text'],keep=False)

    del df_sin_compartidos['Categorias']
    del df_sin_compartidos['Color']

    df_sin_compartidos2 = pd.concat([df_sin_compartidos,df_palabras_a_sacar])

    df_sin_compartidos2 = df_sin_compartidos2.drop_duplicates(['Text'],keep=False)

    df_sin_compartidos2.sort_values(by='Size', inplace=True,ascending=False)
    df_sin_compartidos2 = df_sin_compartidos2[~df_sin_compartidos2['Text'].str.startswith('Https')]
    
    

    return df_sin_compartidos2

# Define your script here
def process_csvs(df_datos_contados, df_visualizado, df_palabras_a_sacar,dic):
    filtered_df = resolutor(df_datos_contados, df_visualizado,dic)
    removed_data= ver_descarte(df_datos_contados,df_visualizado, df_palabras_a_sacar)
    return filtered_df, removed_data

def contarPalabras(df_datos_crudos):
    aux = df_datos_crudos['Content'].str.cat(sep = ' ')
    word_list = aux.lower().split()
    word_counts = Counter(word_list)

    df_word_counts = pd.DataFrame.from_dict(word_counts, orient='index', columns=['Size'])

    # reset the index and rename the columns
    df_word_counts.reset_index(inplace=True)
    df_word_counts.rename(columns={'index': 'Text'}, inplace=True)
    df_word_counts['Text'] = df_word_counts['Text'].str.title()

    return df_word_counts


def main():
    st.set_page_config(page_title="Procesador de Datos", page_icon=":guardsman:", layout="wide",initial_sidebar_state="expanded")

    dic_options = ['Sentimientos', 'Tematicas']
    selected_dic = st.selectbox("Elegi con que vas a trabajar", dic_options)

    if selected_dic == 'Sentimientos':
        dic = {'positivo': '32cd32', 'negativo': 'ff0000'}
    else:
        dic = {'economia': '32cd32', 'gestion': 'ffd700','politica' : 'a9874a','pueblo':'800080','produccion':'ffa500','corrupcion':'8a1919','exterior':'40e0d0','finanza':'00ff00'}



    st.title("Subi los archivos correspondientes")

    uploaded_file1 = st.file_uploader("Subi el excel con datos crudos", type=["xlsx"])
    uploaded_file2 = st.file_uploader("Subi visualizador datos", type=["xlsx"])
    uploaded_file3 = st.file_uploader("Subi palabras a sacar", type=["xlsx"])

    if uploaded_file1 and uploaded_file2 and uploaded_file3:
        df_datos_crudos = pd.read_excel(uploaded_file1)
        df_datos_contados = contarPalabras(df_datos_crudos)
        df_visualizado = pd.read_excel(uploaded_file2)
        df_palabras_a_sacar = pd.read_excel(uploaded_file3)
        filtered_df, removed_data = process_csvs(df_datos_contados, df_visualizado, df_palabras_a_sacar,dic)
        st.write("Palabras sacadas: ")
        st.dataframe(removed_data.head(70).style.set_properties(**{'text-align': 'left'}).format({'Size': '{:,.0f}'}),width=300)


        if st.button('Sacar @'):
            removed_data2 = removed_data[~removed_data['Text'].str.startswith('@')]
            st.dataframe(removed_data2.head(70).style.set_properties(**{'text-align': 'left'}).format({'Size': '{:,.0f}'}),width=300)
    
        if st.button('Dejar solo @'):
            removed_data3 = removed_data[removed_data['Text'].str.startswith('@')]
            st.dataframe(removed_data3.head(70).style.set_properties(**{'text-align': 'left'}).format({'Size': '{:,.0f}'}),width=300)
    
        st.write("Poner en el word art: ")
        filtered_df = filtered_df.rename(columns={'Color':'Cantidad', 'Size':'Color'})

        st.table(filtered_df.reset_index(drop=True).style.set_table_styles([
            {'selector': 'table', 'props': [('border', '2px solid black'),
                                            ('text-align', 'center'),
                                            ('font-size', '20px'),
                                            ('background-color', 'white')]},
            {'selector': 'th', 'props': [('display','none')]},
            {'selector': 'td', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
        ]))


        color_size_sum = filtered_df.groupby('Color')['Cantidad'].sum()

        if selected_dic == 'Sentimientos':
            color_size_sum = color_size_sum.rename({'32cd32': 'Positivo', 'ff0000':'Negativo'})
        else:
            color_size_sum = color_size_sum.rename({'32cd32': 'Economía', 'ffd700': 'Gestión','a9874a' : 'Política','800080':'Pueblo','ffa500':'Producción','8a1919':'Corrupción','40e0d0':'Exterior','00ff00':'Finanza'})



        color_size_sum_df = pd.DataFrame(color_size_sum)
        color_size_sum_df["Porcentajes"]  = color_size_sum_df["Cantidad"].div(color_size_sum_df["Cantidad"].sum())*100
        st.table(color_size_sum_df.style.format({'Cantidad': '{:,.0f}'}).set_table_styles([
            {'selector': 'table', 'props': [('border', '2px solid black'),
                                            ('text-align', 'center'),
                                            ('font-size', '20px'),
                                            ('background-color', 'white')]},
            {'selector': 'th', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
            {'selector': 'td', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
        ]))



main()
