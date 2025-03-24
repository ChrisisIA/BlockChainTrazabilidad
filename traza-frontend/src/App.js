import { useState } from 'react';
import './App.css'; // Opcional: para estilos básicos

import Header from './components/Header';
import './components/Header.css'; // Asegúrate de importar los estilos


function App() {
  const [inputText, setInputText] = useState(''); // Guarda el texto del input
  const [apiUrl, setApiUrl] = useState(''); // URL generada
  const [data, setData] = useState(null); // Almacena el JSON
  const [loading, setLoading] = useState(false); // Estado de carga
  

  // Tu URL base (ajústala a tu necesidad)
  const BASE_URL = 'https://api.gateway.ethswarm.org/bzz/';

  const handleSubmit = (e) => {
    e.preventDefault(); // Evita que el formulario recargue la página
    if (!inputText.trim()) return; // Evita enviar texto vacío

    const finalUrl = `${BASE_URL}${inputText}`; // Construye la URL final
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
      <h1>Buscador de datos JSON</h1>
      
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
          <h2>Resultados:</h2>
          <pre>{JSON.stringify(data, null, 2)}</pre> {/* Formato legible */}
        </div>
      ) : (
        apiUrl && !loading && <p>No se encontraron datos.</p>
      )}
    </div>
  );
}

export default App;