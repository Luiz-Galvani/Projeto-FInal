import streamlit as st
from data.CriacaoBD import criarTable
from streamlit import config as _config

_config.set_option("theme.base", "light")
_config.set_option("theme.primaryColor", "#ff4b4b")
_config.set_option("theme.backgroundColor", "#ffffff")
_config.set_option("theme.secondaryBackgroundColor", "#f0f2f6")
_config.set_option("theme.textColor", "#31333F")

def main():
    criarTable()
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    dashboard_page = st.Page("frontend/dashboard.py", title="Dashboard", icon="🏠", url_path="/dashboard")
    aeroportos = st.Page("frontend/aeroportos.py", title="Aeroportos", icon="👥", url_path="/aeroportos") 
    empresas = st.Page("frontend/empresas.py", title="empresas", icon="💪", url_path="/empresas") 
    eficiencia = st.Page("frontend/eficiencia.py", title="eficiencia", icon="💰", url_path="/eficiencia")

    pg = st.navigation([dashboard_page])

    pg = st.navigation([
            dashboard_page,
            aeroportos,
            empresas,
            eficiencia
        ])
    
    pg.run()

if __name__ == "__main__":
    main()