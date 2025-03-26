import { useState } from 'react';
import './App.css';

import Header from './components/Header';
import './components/Header.css';


function App() {
  const [inputText, setInputText] = useState(''); // Guarda el texto del input
  const [apiUrl, setApiUrl] = useState(''); // URL generada
  const [data, setData] = useState(null); // Almacena el JSON
  const [loading, setLoading] = useState(false); // Estado de carga
  

  // Tu URL base (ajústala a tu necesidad)
  const BASE_URL = 'https://api.gateway.ethswarm.org/bzz/';

  const handleSubmit = (e) => {
    e.preventDefault(); 
    if (!inputText.trim()) return; 

    const finalUrl = `${BASE_URL}${inputText}`; 
    setApiUrl(finalUrl);
    fetchData(finalUrl);
  };

  const fetchData = async (url) => {
    setLoading(true);
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Error al obtener los datos');
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error('Error:', error);
      setData(null); // Limpia datos en caso de error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <Header />
      <h1>Enter the tickbarr Hash</h1>
      
      {/* Formulario con input y botón */}
      <form onSubmit={handleSubmit} className="search-box">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ingresa tu búsqueda..."
        />
        <button type="submit">Buscar</button>
      </form>

      {/* Muestra la URL generada */}
      {apiUrl && (
        <div className="url-display">
          <strong>URL solicitada:</strong> {apiUrl}
        </div>
      )}

      {/* Muestra el estado de carga */}
      {loading && <p>Cargando datos...</p>}

      {/* Muestra los datos JSON o un mensaje de error */}
      {data ? (
        <div className="json-result">
          {/* Sección Cliente */}
          <div className="data-section">
            <h2 className="section-title">Cliente</h2>
            <div className="section-content">
              <p><strong>Código Barras:</strong> {data.tztotrazwebinfo[0].TTICKBARR}</p>
              <p><strong>Nombre Cliente:</strong> {data.tztotrazwebinfo[0].TNOMBCLIE}</p>
            </div>
          </div>

          {/* Sección Atributos */}
          <div className="data-section">
            <h2 className="section-title">Atributos</h2>
            <div className="section-content">
              <p><strong>Código Etiqueta:</strong> {data.tztotrazwebinfo[0].TCODIETIQCLIE}</p>
              <p><strong>Talla:</strong> {data.tztotrazwebinfo[0].TCODITALL}</p>
            </div>
          </div>

          {/* Sección Información Adicional */}
          <div className="data-section">
            <h2 className="section-title">Información Adicional</h2>
            <div className="section-content">
              <p><strong>Descripción Prenda:</strong> {data.tztotrazwebinfo[0].TDESCPREN}</p>
              <p><strong>Tipo Prenda:</strong> {data.tztotrazwebinfo[0].TDESCTIPOPREN}</p>
              <p><strong>Fecha Ingreso:</strong> {data.tztotrazwebinfo[0].TFECHINGRESTA}</p>
            </div>
          </div>
        </div>
      ) : (
        apiUrl && !loading && <p>No se encontraron datos.</p>
      )}
    </div>
  );
}

export default App;