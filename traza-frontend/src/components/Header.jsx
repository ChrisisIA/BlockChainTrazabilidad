import { FaWarehouse} from 'react-icons/fa';
import { CiBarcode } from "react-icons/ci";
import { PiInfoBold, PiYarn } from "react-icons/pi";
import { LiaTshirtSolid } from "react-icons/lia";
import { GiSewingMachine, GiStickFrame } from "react-icons/gi";
import { RiScissorsCutLine, RiPaintLine} from "react-icons/ri";
import { GrLanguage } from "react-icons/gr";

const Header = () => {
// Función placeholder para los clicks (la personalizarás luego)
const handleIconClick = (iconName) => {
console.log(`Icono clickeado: ${iconName}`);
// Aquí añadirás la lógica para cada ícono
};

// Array de íconos para cada fila
const row1Icons = [
{ icon: <CiBarcode size={70}/>, name: 'NEW TICKET' },
{ icon: <PiInfoBold size={70}/>, name: 'GARMENT Info' },
{ icon: <FaWarehouse size={70}/>, name: 'WAREHOUSE' },
{ icon: <LiaTshirtSolid size={70}/>, name: 'GARMENT FINISHING' },
{ icon: <GiSewingMachine size={70} />, name: 'SEWING' }
];

const row2Icons = [
{ icon: <RiScissorsCutLine size={70}/>, name: 'CUTTING' },
{ icon: <RiPaintLine size={70} />, name: 'FABRIC DYEING' },
{ icon: <GiStickFrame size={70}/>, name: 'KNITTING' },
{ icon: <PiYarn size={70}/>, name: 'YARN SUPPLYING' },
{ icon: <GrLanguage size={30}/>, name: 'Language' }
];

return (
<header className="header">
 {/* Primera fila de íconos */}
 <div className="icon-row">
   {row1Icons.map((item, index) => (
     <div 
       key={index} 
       className="icon-container"
       onClick={() => handleIconClick(item.name)}
     >
       {item.icon}
       <span className="icon-tooltip">{item.name}</span>
     </div>
   ))}
 </div>

 {/* Segunda fila de íconos */}
 <div className="icon-row">
   {row2Icons.map((item, index) => (
     <div 
       key={index} 
       className="icon-container"
       onClick={() => handleIconClick(item.name)}
     >
       {item.icon}
       <span className="icon-tooltip">{item.name}</span>
     </div>
   ))}
 </div>
</header>
);
};

export default Header;