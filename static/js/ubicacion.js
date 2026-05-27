'use strict';

/* Datos geográficos de Perú: Departamento → Provincia → [Distritos] */
const PERU_GEO = {
  "Amazonas": {
    "Bagua":                ["Aramango", "Bagua", "Copallín", "El Parco", "Imaza", "La Peca"],
    "Bongará":              ["Chisquilla", "Churuja", "Corosha", "Cuispes", "Florida", "Jazán", "Jumbilla", "Recta", "San Carlos", "Shipasbamba", "Valera", "Yambrasbamba"],
    "Chachapoyas":          ["Asunción", "Balsas", "Chachapoyas", "Cheto", "Chiliquín", "Chuquibamba", "Granada", "Huancas", "La Jalca", "Leimebamba", "Levanto", "Magdalena", "Mariscal Castilla", "Molinopampa", "Montevideo", "Olleros", "Quinjalca", "San Francisco de Daguas", "San Isidro de Maino", "Soloco", "Sonche"],
    "Condorcanqui":         ["El Cenepa", "Nieva", "Río Santiago"],
    "Luya":                 ["Camporredondo", "Cocabamba", "Colcamar", "Conila", "Inguilpata", "Lamud", "Longuita", "Lonya Chico", "Luya", "Luya Viejo", "María", "Ocalli", "Ocumal", "Pisuquia", "Providencia", "San Cristóbal", "San Francisco del Yeso", "San Jerónimo", "San Juan de Lopecancha", "Santa Catalina", "Santo Tomás", "Tingo", "Trita"],
    "Rodríguez de Mendoza": ["Chirimoto", "Cochamal", "Huambo", "Limabamba", "Longar", "Mariscal Benavides", "Milpuc", "Omia", "San Nicolás", "Santa Rosa", "Totora", "Vista Alegre"],
    "Utcubamba":            ["Bagua Grande", "Cajaruro", "Cumba", "El Milagro", "Jamalca", "Lonya Grande", "Yamon"]
  },
  "Áncash": {
    "Aija":                        ["Aija", "Coris", "Huacllán", "La Merced", "Succha"],
    "Antonio Raimondi":            ["Aczo", "Chaccho", "Chingas", "Llamellín", "Mirgas", "San Juan de Rontoy"],
    "Asunción":                    ["Acochaca", "Chacas"],
    "Bolognesi":                   ["Aquia", "Bolognesi", "Canis", "Chiquián", "Corpanqui", "Huallanca", "Huasta", "Huayllacayán", "La Primavera", "Mangas", "Pacllon", "San Miguel de Corpanqui", "Ticllos"],
    "Carhuaz":                     ["Acopampa", "Amashca", "Anta", "Ataquero", "Carhuaz", "Marcará", "Pampas", "San Miguel de Aco", "Shilla", "Tinco", "Yungar"],
    "Carlos Fermín Fitzcarrald":   ["San Luis", "San Nicolás", "Yauya"],
    "Casma":                       ["Buena Vista Alta", "Casma", "Comandante Noel", "Yaután"],
    "Corongo":                     ["Aco", "Bambas", "Corongo", "Cusca", "La Pampa", "Pinto", "Yanac"],
    "Huaraz":                      ["Cochabamba", "Colcabamba", "Huanchay", "Huaraz", "Independencia", "Jangas", "La Libertad", "Llanganuco", "Pampas Grande", "Paucará", "Pira", "Tarica"],
    "Huari":                       ["Anra", "Cajay", "Chavín de Huántar", "Huacachi", "Huacchis", "Huachis", "Huantar", "Huari", "Masín", "Paucas", "Ponto", "Rahuapampa", "Rapayán", "San Marcos", "San Pedro de Chaná", "Uco"],
    "Huarmey":                     ["Cochapetí", "Culebras", "Huarmey", "Huayán", "Malvas"],
    "Huaylas":                     ["Caraz", "Huallanca", "Huata", "Huaylas", "Mato", "Pamparomas", "Pueblo Libre", "Santa Cruz", "Santo Toribio", "Yuracmarca"],
    "Mariscal Luzuriaga":          ["Casca", "Eleazar Guzmán Barrón", "Fidel Olivas Escudero", "Llumpa", "Lucma", "Musga", "Piscobamba"],
    "Ocros":                       ["Acas", "Cajamarquilla", "Carhuapampa", "Cochas", "Congas", "Llipa", "Ocros", "San Cristóbal de Raján", "San Pedro", "Santiago de Chilcas"],
    "Pallasca":                    ["Bolognesi", "Cabana", "Conchucos", "Huacaschuque", "Huandoval", "Lacabamba", "Llapo", "Pallasca", "Pampas", "Santa Rosa", "Tauca"],
    "Pomabamba":                   ["Huayllan", "Parobamba", "Pomabamba", "Quinuabamba"],
    "Recuay":                      ["Catac", "Cotaparaco", "Huayllapampa", "Llacllin", "Marián", "Pampas Chico", "Pampas Grande", "Recuay", "Tapacocha", "Ticapampa"],
    "Santa":                       ["Cáceres del Perú", "Chimbote", "Coishco", "Macate", "Moro", "Nepeña", "Nuevo Chimbote", "Samanco", "Santa"],
    "Sihuas":                      ["Acobamba", "Alfonso Ugarte", "Cashapampa", "Chingalpo", "Huayllabamba", "Mollepata", "Quiches", "Ragash", "San Juan", "Sicsibamba", "Sihuas"],
    "Yungay":                      ["Cascapara", "Mancos", "Matacoto", "Quillo", "Ranrahirca", "Shupluy", "Yanama", "Yungay"]
  },
  "Apurímac": {
    "Abancay":    ["Abancay", "Chacoche", "Circa", "Curahuasi", "Huanipaca", "Lambrama", "Pichirhua", "San Pedro de Cachora", "Tamburco"],
    "Andahuaylas":["Andarapa", "Chiara", "Huancarama", "Huancaray", "Huayana", "Kaquiabamba", "Kishuara", "Pacobamba", "Pacucha", "Pampachiri", "Pomacocha", "San Antonio de Cachi", "San Jerónimo", "San Miguel de Chaccrampa", "Santa María de Chicmo", "Talavera", "Tumay Huaraca", "Turpo"],
    "Antabamba":  ["Antabamba", "El Oro", "Huaquirca", "Juan Espinoza Medrano", "Oropesa", "Pachaconas", "Sabaino"],
    "Aymaraes":   ["Capaya", "Caraybamba", "Chalhuanca", "Chapimarca", "Colcabamba", "Cotaruse", "Huayllo", "Justo Apu Sahuaraura", "Lucre", "Pocohuanca", "Sañayca", "Soraya", "Tapairihua", "Tintay", "Toraya", "Yanaca"],
    "Chincheros": ["Anco-Huallo", "Chincheros", "El Porvenir", "Huaccana", "Ocobamba", "Ongoy", "Ranracancha", "Rocchac", "Uranmarca"],
    "Cotabambas": ["Cotabambas", "Coyllurqui", "Haquira", "Mara", "Tambobamba"],
    "Grau":       ["Chuquibambilla", "Curpahuasi", "Gamarra", "Huayllati", "Mamara", "Micaela Bastidas", "Pataypampa", "Progreso", "San Antonio", "Santa Rosa", "Turpay", "Vilcabamba", "Virundo"]
  },
  "Arequipa": {
    "Arequipa":    ["Alto Selva Alegre", "Arequipa", "Cayma", "Cerro Colorado", "Characato", "Chiguata", "Hunter", "Jacobo Hunter", "José Luis Bustamante y Rivero", "La Joya", "Mariano Melgar", "Miraflores", "Mollebaya", "Paucarpata", "Pocsi", "Polobaya", "Quequeña", "Sabandía", "Sachaca", "San Juan de Siguas", "San Juan de Tarucani", "Santa Isabel de Siguas", "Santa Rita de Siguas", "Socabaya", "Tiabaya", "Uchumayo", "Vitor", "Yanahuara", "Yarabamba", "Yura"],
    "Camaná":      ["Camaná", "José María Quimper", "Mariano Nicolás Valcárcel", "Mariscal Cáceres", "Nicolás de Pierola", "Ocoña", "Quilca", "Samuel Pastor"],
    "Caravelí":    ["Acarí", "Atico", "Atiquipa", "Bella Unión", "Cahuacho", "Caravelí", "Chala", "Chaparra", "Huanuhuanu", "Jaqui", "Lomas", "Quicacha", "Yauca"],
    "Castilla":    ["Alca", "Aplao", "Ayo", "Choco", "Huancarqui", "Machaguay", "Orcopampa", "Pampacolca", "Tipan", "Uñon", "Uraca", "Viraco"],
    "Caylloma":    ["Achoma", "Cabanaconde", "Callalli", "Caylloma", "Chivay", "Coporaque", "Huambo", "Huanca", "Ichupampa", "Lari", "Lluta", "Maca", "Madrigal", "Majes", "San Antonio de Chuca", "Sibayo", "Tapay", "Tisco", "Tuti", "Yanque"],
    "Condesuyos":  ["Andaray", "Cayarani", "Chichas", "Chuquibamba", "Iray", "Río Grande", "Salamanca", "Yanaquihua"],
    "Islay":       ["Cocachacra", "Dean Valdivia", "El Fiscal", "Islay", "Mejía", "Mollendo", "Punta de Bombón"],
    "La Unión":    ["Alca", "Charcana", "Cotahuasi", "Huaynacotas", "Pampamarca", "Puyca", "Quechualla", "Sayla", "Tauria", "Tomepampa", "Toro"]
  },
  "Ayacucho": {
    "Cangallo":          ["Cangallo", "Chuschi", "Los Morochucos", "María Parado de Bellido", "Paras", "Totos"],
    "Huamanga":          ["Acocro", "Acos Vinchos", "Andrés Avelino Cáceres Dorregaray", "Ayacucho", "Carmen Alto", "Chiara", "Jesús Nazareno", "Ocros", "Pacaycasa", "Quinua", "San José de Ticllas", "San Juan Bautista", "Santiago de Pischa", "Socos", "Tambillo", "Vinchos", "Wari"],
    "Huanca Sancos":     ["Carapo", "Sacsamarca", "Sancos", "Santiago de Lucanamarca"],
    "Huanta":            ["Ayahuanco", "Canayre", "Chaca", "Huamanguilla", "Huanta", "Huanhuanca", "Iguaín", "Llochegua", "Luricocha", "Pucacolpa", "Santillana", "Sivia", "Uchuraccay"],
    "La Mar":            ["Anco", "Ayna", "Chilcas", "Chungui", "Luisiana", "Oronccoy", "San Miguel", "Santa Rosa", "Tambo", "Unión Progreso"],
    "Lucanas":           ["Aucara", "Cabana", "Carmen Salcedo", "Chaviña", "Chipao", "Huac-Huas", "Laramate", "Leoncio Prado", "Llauta", "Lucanas", "Ocaña", "Otoca", "Puquio", "Saisa", "San Cristóbal", "San Juan", "San Pedro", "San Pedro de Palco", "Sancos", "Santa Ana de Huaycahuacho", "Santa Lucía"],
    "Parinacochas":      ["Chumpi", "Coracora", "Coronel Castañeda", "Pacapausa", "Puyusca", "San Francisco de Ravacayco", "Upahuacho"],
    "Páucar del Sara Sara": ["Colta", "Corculla", "Lampa", "Marcabamba", "Oyolo", "Pararca", "Pausa", "San Javier de Alpabamba", "San José de Ushua", "Sara Sara"],
    "Sucre":             ["Belén", "Chalcos", "Chilcayoc", "Huacaña", "Morcolla", "Paico", "San Salvador de Quije", "Santiago de Paucaray", "Soras"],
    "Víctor Fajardo":    ["Accomarca", "Apongo", "Asquipata", "Canaria", "Cayara", "Colca", "Huancapi", "Huancaraylla", "Huaya", "Sarhua", "Vilcanchos"],
    "Vilcas Huamán":     ["Accomarca", "Carhuanca", "Concepción", "Huambalpa", "Independencia", "Saurama", "Vischongo", "Vilcas Huamán"]
  },
  "Cajamarca": {
    "Cajabamba":   ["Cachachi", "Cajabamba", "Condebamba", "Sitacocha"],
    "Cajamarca":   ["Asunción", "Cajamarca", "Chetilla", "Cospán", "Encañada", "Jesús", "Llacanora", "Los Baños del Inca", "Magdalena", "Matara", "Namora", "San Juan"],
    "Celendín":    ["Celendín", "Chumuch", "Cortegana", "Huasmin", "Jorge Chávez", "José Gálvez", "Miguel Iglesias", "Oxamarca", "Sorochuco", "Sucre", "Utco", "La Libertad de Pallán"],
    "Chota":       ["Anguía", "Chadín", "Chiguirip", "Chimban", "Choropampa", "Cochabamba", "Conchan", "Chota", "Huambos", "Lajas", "Llama", "Miracosta", "Paccha", "Pion", "Querocoto", "San Juan de Licupis", "Tacabamba", "Tocmoche", "Chalamarca"],
    "Contumazá":   ["Chilete", "Contumazá", "Cupisnique", "Guzmango", "San Benito", "Santa Cruz de Toledo", "Tantarica", "Yonán"],
    "Cutervo":     ["Callayuc", "Choros", "Cujillo", "Cutervo", "La Ramada", "Pimpingos", "Querecotillo", "San Andrés de Cutervo", "San Juan de Cutervo", "San Luis de Lucma", "Santa Cruz", "Santo Domingo de la Capilla", "Santo Tomás", "Socota", "Toribio Casanova"],
    "Hualgayoc":   ["Bambamarca", "Chugur", "Hualgayoc"],
    "Jaén":        ["Bellavista", "Chontali", "Colasay", "Huabal", "Jaén", "Las Pirias", "Pucará", "Sallique", "San Felipe", "San José del Alto", "Santa Rosa"],
    "San Ignacio": ["Chirinos", "Huarango", "La Coipa", "Namballe", "San Ignacio", "San José de Lourdes", "Tabaconas"],
    "San Marcos":  ["Chancay", "Eduardo Villanueva", "Gregorio Pita", "Ichocan", "José Manuel Quiroz", "José Sabogal", "Pedro Gálvez"],
    "San Miguel":  ["Bolívar", "Calquis", "Catilluc", "El Prado", "La Florida", "Llapa", "Nanchoc", "Niepos", "San Gregorio", "San Miguel", "San Silvestre de Cochan", "Tongod", "Unión Agua Blanca"],
    "San Pablo":   ["Kuntur Wasi", "San Bernardino", "San Luis", "San Pablo", "Tumbaden"],
    "Santa Cruz":  ["Andabamba", "Catache", "Chancaybaños", "La Esperanza", "Ninabamba", "Pulán", "Saucepampa", "Sexi", "Uticyacu", "Santa Cruz", "Yauyucán"]
  },
  "Callao": {
    "Callao": ["Bellavista", "Callao", "Carmen de la Legua Reynoso", "La Perla", "La Punta", "Mi Perú", "Ventanilla"]
  },
  "Cusco": {
    "Acomayo":       ["Acomayo", "Acopia", "Acos", "Mosoc Llacta", "Pomacanchi", "Rondocan", "Sangarará"],
    "Anta":          ["Ancahuasi", "Anta", "Cachimayo", "Chinchaypujio", "Huarocondo", "Limatambo", "Mollepata", "Pucyura", "Zurite"],
    "Calca":         ["Calca", "Coya", "Lamay", "Lares", "Pisac", "San Salvador", "Taray", "Yanatile"],
    "Canas":         ["Checca", "Kunturkanki", "Langui", "Layo", "Pampamarca", "Quehue", "Túpac Amaru", "Yanaoca"],
    "Canchis":       ["Checacupe", "Combapata", "Maranganí", "Pitumarca", "San Pablo", "San Pedro", "Sicuani", "Tinta"],
    "Chumbivilcas":  ["Capacmarca", "Chamaca", "Colquemarca", "Livitaca", "Llusco", "Quiñota", "Santo Tomás", "Velille"],
    "Cusco":         ["Ccorca", "Cusco", "Poroy", "San Jerónimo", "San Sebastián", "Santiago", "Saylla", "Wanchaq"],
    "Espinar":       ["Alto Pichigua", "Condoroma", "Coporaque", "Espinar", "Ocoruro", "Pallpata", "Pichigua", "Suyckutambo"],
    "La Convención": ["Echarate", "Huayopata", "Inkawasi", "Kimbiri", "Maranura", "Megantoni", "Ocobamba", "Pichari", "Quellouno", "Santa Ana", "Santa Teresa", "Vilcabamba", "Villa Kintiarina", "Villa Virgen"],
    "Paruro":        ["Accha", "Ccapi", "Colcha", "Huanoquite", "Omacha", "Paccaritambo", "Pillpinto", "Yaurisque", "Paruro"],
    "Paucartambo":   ["Caicay", "Challabamba", "Colquepata", "Huancarani", "Kosñipata", "Paucartambo"],
    "Quispicanchi":  ["Andahuaylillas", "Camanti", "Ccarhuayo", "Ccatca", "Cusipata", "Huaro", "Lucre", "Marcapata", "Ocongate", "Oropesa", "Quiquijana", "Urcos"],
    "Urubamba":      ["Chinchero", "Huayllabamba", "Machupicchu", "Maras", "Ollantaytambo", "Urubamba", "Yucay"]
  },
  "Huancavelica": {
    "Acobamba":      ["Acobamba", "Andabamba", "Anta", "Caja", "Marcas", "Paucara", "Pomacocha", "Rosario"],
    "Angaraes":      ["Anchonga", "Callanmarca", "Ccochaccasa", "Chincho", "Congalla", "Huanca-Huanca", "Julcamarca", "Lircay", "San Antonio de Antaparco", "Santo Tomás de Pata", "Secclla"],
    "Castrovirreyna":["Arma", "Aurahua", "Capillas", "Castrovirreyna", "Chupamarca", "Cocas", "Huachos", "Huamatambo", "Mollepampa", "San Juan", "Santa Ana", "Ticrapo"],
    "Churcampa":     ["Anco", "Chinchihuasi", "Churcampa", "El Carmen", "La Merced", "Locroja", "Paucarbamba", "San Miguel de Mayocc", "San Pedro de Coris", "Zupayuq"],
    "Huancavelica":  ["Acobambilla", "Acoria", "Conayca", "Cuenca", "Huachocolpa", "Huayllahuara", "Huancavelica", "Izcuchaca", "Laria", "Manta", "Mariscal Cáceres", "Moya", "Nuevo Occoro", "Palca", "Pilchaca", "Vilca", "Yauli"],
    "Huaytará":      ["Ayavi", "Córdova", "Huayacundo Arma", "Huaytará", "Laramarca", "Ocoyo", "Pilpichaca", "Querco", "Quito-Arma", "San Antonio de Cusicancha", "San Francisco de Sangayaico", "San Isidro", "Santiago de Chocorvos", "Santiago de Quirahuará", "Santo Domingo de Capillas", "Tambo"],
    "Tayacaja":      ["Acostambo", "Acraquia", "Ahuaycha", "Andaymarca", "Colcabamba", "Daniel Hernández", "Huachocolpa", "Huaribamba", "Ñahuimpuquio", "Pazos", "Pichos", "Pampas", "Quishuar", "Salcabamba", "Salcahuasi", "San Marcos de Rocchac", "Surcubamba", "Tintay Puncu", "Tocas", "Zarka"]
  },
  "Huánuco": {
    "Ambo":          ["Ambo", "Cayna", "Colpas", "Conchamarca", "Huácar", "San Francisco", "San Rafael", "Tomay Kichwa"],
    "Dos de Mayo":   ["Chuquis", "La Unión", "Marías", "Pachas", "Quivilla", "Ripan", "Shunqui", "Sillapata", "Yanas"],
    "Huacaybamba":   ["Canchabamba", "Cochabamba", "Huacaybamba", "Pinra"],
    "Huamalíes":     ["Arancay", "Chavin de Pariarca", "Huacrachuco", "Jacas Grande", "Jircan", "Llata", "Miraflores", "Monzón", "Punchao", "Puños", "Singa", "Tantamayo"],
    "Huánuco":       ["Amarilis", "Chinchao", "Churubamba", "Huánuco", "Margos", "Quisqui", "San Francisco de Cayrán", "San Pedro de Chaulan", "Santa María del Valle", "Yarumayo"],
    "Lauricocha":    ["Baños", "Jesús", "Jivia", "Queropalca", "Rondos", "San Francisco de Asís", "San Miguel de Cauri"],
    "Leoncio Prado": ["Daniel Alomía Robles", "Hermilio Valdizán", "José Crespo y Castillo", "Luyando", "Mariano Dámaso Beraún", "Pucayacu", "Castillo Grande", "Rupa-Rupa"],
    "Marañón":       ["Cholón", "Huacrachuco", "San Buenaventura"],
    "Pachitea":      ["Chaglla", "Molino", "Panao", "Umari"],
    "Puerto Inca":   ["Codo del Pozuzo", "Honoria", "Puerto Inca", "Tournavista", "Yuyapichis"],
    "Yarowilca":     ["Aparicio Pomares", "Cahuac", "Chacabamba", "Chavinillo", "Choras", "Jacas Chico", "Obas", "Pampamarca"]
  },
  "Ica": {
    "Chincha": ["Alto Larán", "Chavin", "Chincha Alta", "Chincha Baja", "El Carmen", "Grocio Prado", "Hoja Redonda", "Pueblo Nuevo", "San Juan de Yanac", "San Pedro de Huacarpana", "Sunampe", "Tambo de Mora"],
    "Ica":     ["Ica", "La Tinguiña", "Los Aquijes", "Ocucaje", "Pachacútec", "Parcona", "Pueblo Nuevo", "Salas", "San José de Los Molinos", "San Juan Bautista", "Santiago", "Subtanjalla", "Tate", "Yauca del Rosario"],
    "Nazca":   ["Changuillo", "El Ingenio", "Marcona", "Nazca", "Vista Alegre"],
    "Palpa":   ["Llipata", "Palpa", "Río Grande", "Santa Cruz", "Tibillo"],
    "Pisco":   ["Huancano", "Humay", "Independencia", "Paracas", "Pisco", "San Andrés", "San Clemente", "Tupac Amaru Inca"]
  },
  "Junín": {
    "Chanchamayo": ["Chanchamayo", "Perené", "Pichanaqui", "San Luis de Shuaro", "San Ramón", "Vitoc"],
    "Chupaca":     ["Ahuac", "Chongos Bajo", "Chupaca", "Huachac", "Huamancaca Chico", "San Juan de Yscos", "San Telmo de Paccha", "Tres de Diciembre", "Yanacancha"],
    "Concepción":  ["Aco", "Andamarca", "Chambara", "Cochas", "Comas", "Concepción", "Heroínas Toledo", "Manzanares", "Mariscal Castilla", "Matahuasi", "Mito", "Nueve de Julio", "Orcotuna", "San José de Quero", "Santa Rosa de Ocopa"],
    "Huancayo":    ["Carhuacallanga", "Carhuamayo", "Chacapampa", "Chicche", "Chilca", "Chongos Alto", "Chupuro", "Colca", "Cullhuas", "El Tambo", "Huacrapuquio", "Hualhuas", "Huancán", "Huancayo", "Huasicancha", "Huayucachi", "Ingenio", "Pariahuanca", "Pilcomayo", "Pucará", "Quilcas", "San Agustín de Cajas", "San Jerónimo de Tunán", "Saño", "Sapallanga", "Sicaya", "Viques"],
    "Jauja":       ["Acolla", "Apata", "Ataura", "Canchayllo", "Curicaca", "El Mantaro", "Huamali", "Huaripampa", "Huertas", "Janjaillo", "Jauja", "Julcán", "Leonor Ordóñez", "Llocllapampa", "Marco", "Masma", "Masma Chicche", "Molinos", "Monobamba", "Muqui", "Muquiyauyo", "Paca", "Paccha", "Pancan", "Parco", "Pomacancha", "Ricran", "San Lorenzo", "San Pedro de Chunán", "Sausa", "Sincos", "Tunan Marca", "Yauli", "Yauyos"],
    "Junín":       ["Carhuamayo", "Junín", "Ondores", "Ulcumayo"],
    "Satipo":      ["Coviriali", "Llaylla", "Mazamari", "Pampa Hermosa", "Pangoa", "Río Negro", "Río Tambo", "Satipo", "Vizcatán del Ene"],
    "Tarma":       ["Acobamba", "Huaricolca", "Huasahuasi", "La Unión", "Palca", "Palcamayo", "San Pedro de Cajas", "Tapo", "Tarma"],
    "Yauli":       ["Chacapalpa", "Huay-Huay", "La Oroya", "Marcapomacocha", "Morococha", "Paccha", "Santa Bárbara de Carhuacayán", "Santa Rosa de Sacco", "Suitucancha", "Yauli"]
  },
  "La Libertad": {
    "Ascope":           ["Ascope", "Chicama", "Chocope", "Magdalena de Cao", "Paiján", "Rázuri", "Santiago de Cao", "Casa Grande"],
    "Bolívar":          ["Bambamarca", "Bolívar", "Condormarca", "Longotea", "Ucuncha", "Uchumarca"],
    "Chepén":           ["Chepén", "Malabrigo", "Pacanga", "Pueblo Nuevo"],
    "Gran Chimú":       ["Cascas", "Lucma", "Marmot", "Sayapullo"],
    "Julcán":           ["Carabamba", "Calamarca", "Huaso", "Julcán"],
    "Otuzco":           ["Agallpampa", "Charat", "Huaranchal", "La Cuesta", "Mache", "Otuzco", "Paranday", "Salpo", "Sinsicap", "Usquil"],
    "Pacasmayo":        ["Guadalupe", "Jequetepeque", "Pacasmayo", "San Pedro de Lloc", "Pacanga"],
    "Pataz":            ["Buldibuyo", "Chillia", "Huancaspata", "Huaylillas", "Huayo", "Ongón", "Parcoy", "Pataz", "Pías", "Santiago de Challas", "Taurija", "Tayabamba", "Urpay"],
    "Sánchez Carrión":  ["Chugay", "Cochorco", "Curgos", "Huamachuco", "Marcabal", "Sanagoran", "Sarin", "Sartimbamba"],
    "Santiago de Chuco":["Angasmarca", "Cachicadan", "Mollebamba", "Mollepata", "Quiruvilca", "Santa Cruz de Chuca", "Sitabamba", "Santiago de Chuco"],
    "Trujillo":         ["El Porvenir", "Florencia de Mora", "Huanchaco", "La Esperanza", "Laredo", "Moche", "Poroto", "Salaverry", "Simbal", "Trujillo", "Víctor Larco Herrera"],
    "Virú":             ["Chao", "Guadalupito", "Virú"]
  },
  "Lambayeque": {
    "Chiclayo":   ["Cayaltí", "Chiclayo", "Chongoyape", "Eten", "Eten Puerto", "José Leonardo Ortiz", "La Victoria", "Lagunas", "Monsefú", "Nueva Arica", "Oyotún", "Picsi", "Pimentel", "Pomalca", "Pucalá", "Reque", "Santa Rosa", "Saña", "Tumán"],
    "Ferreñafe":  ["Cañaris", "Ferreñafe", "Incahuasi", "Manuel Antonio Mesones Muro", "Pítipo", "Pueblo Nuevo"],
    "Lambayeque": ["Chóchope", "Íllimo", "Jayanca", "Lambayeque", "Mochumí", "Mórrope", "Motupe", "Olmos", "Pacora", "Salas", "San José", "Túcume"]
  },
  "Lima": {
    "Barranca":   ["Barranca", "Paramonga", "Pativilca", "Supe", "Supe Puerto"],
    "Cajatambo":  ["Cajatambo", "Copa", "Gorgor", "Huancapon", "Mangas"],
    "Canta":      ["Arahuay", "Canta", "Huamantanga", "Huaros", "Lachaqui", "San Buenaventura", "Santa Rosa de Quives"],
    "Cañete":     ["Asia", "Calango", "Cerro Azul", "Chilca", "Coayllo", "Imperial", "Lunahuaná", "Mala", "Nuevo Imperial", "Pacarán", "Quilmaná", "San Antonio", "San Luis", "San Vicente de Cañete", "Santa Cruz de Flores", "Zúñiga"],
    "Huaral":     ["Atavillos Alto", "Atavillos Bajo", "Aucallama", "Chancay", "Huaral", "Ihuarí", "Lampián", "Pacaraos", "San Miguel de Acos", "Santa Cruz de Andamarca", "Sumbilca", "Veintisiete de Noviembre"],
    "Huarochirí": ["Antioquia", "Callahuanca", "Carampoma", "Chicla", "Cuenca", "Huachupampa", "Huanza", "Huarochirí", "Lahuaytambo", "Langa", "Laraos", "Mariatana", "Ricardo Palma", "San Andrés de Tupicocha", "San Antonio", "San Bartolomé", "San Damián", "San Juan de Iris", "San Lorenzo de Quinti", "San Mateo", "San Mateo de Otao", "San Pedro de Casta", "Santa Cruz de Cocachacra", "Santa Eulalia", "Santiago de Anchucaya", "Santiago de Tuna", "Santo Domingo de los Olleros", "Surco"],
    "Huaura":     ["Ambar", "Caleta de Carquín", "Checras", "Huacho", "Hualmay", "Huaura", "Leoncio Prado", "Paccho", "Santa Leonor", "Santa María", "Sayan", "Vegueta"],
    "Lima":       ["Ancón", "Ate", "Barranco", "Breña", "Carabayllo", "Chaclacayo", "Chorrillos", "Cieneguilla", "Comas", "El Agustino", "Independencia", "Jesús María", "La Molina", "La Victoria", "Lima", "Lince", "Los Olivos", "Lurigancho", "Lurín", "Magdalena del Mar", "Miraflores", "Pachacámac", "Pucusana", "Pueblo Libre", "Puente Piedra", "Punta Hermosa", "Punta Negra", "Rímac", "San Bartolo", "San Borja", "San Isidro", "San Juan de Lurigancho", "San Juan de Miraflores", "San Luis", "San Martín de Porres", "San Miguel", "Santa Anita", "Santa María del Mar", "Santa Rosa", "Santiago de Surco", "Surquillo", "Villa El Salvador", "Villa María del Triunfo"],
    "Oyón":       ["Andajes", "Caujul", "Cochamarca", "Naván", "Oyón", "Pachangara"],
    "Yauyos":     ["Alis", "Allauca", "Ayauca", "Ayaviri", "Azángaro", "Cacra", "Carania", "Catahuasi", "Chocos", "Cochas", "Colonia", "Hongos", "Huampara", "Huancaya", "Huangáscar", "Huantán", "Huañec", "Laraos", "Lincha", "Madean", "Miraflores", "Omas", "Putinza", "Quinches", "Quinocay", "San Joaquín", "San Pedro de Pilas", "Tanta", "Tauripampa", "Tomas", "Tupe", "Viñac", "Vitis", "Yauyos"]
  },
  "Loreto": {
    "Alto Amazonas":          ["Balsapuerto", "Barranca", "Cahuapanas", "Jeberos", "Lagunas", "Manseriche", "Morona", "Pastaza", "Yurimaguas"],
    "Datem del Marañón":      ["Andoas", "Barranca", "Cahuapanas", "Manseriche", "Morona", "Pastaza"],
    "Loreto":                 ["Nauta", "Parinari", "Tigre", "Trompeteros", "Urarinas"],
    "Mariscal Ramón Castilla": ["Caballococha", "Pebas", "Ramón Castilla", "San Pablo", "Yavarí"],
    "Maynas":                 ["Alto Nanay", "Belén", "Fernando Lores", "Indiana", "Iquitos", "Las Amazonas", "Mazan", "Napo", "Punchana", "Putumayo", "San Juan Bautista", "Torres Causana"],
    "Putumayo":               ["Putumayo", "Rosa Panduro", "Teniente Manuel Clavero", "Yaguas"],
    "Requena":                ["Alto Tapiche", "Capelo", "Emilio San Martín", "Jenaro Herrera", "Maquia", "Puinahua", "Requena", "Saquena", "Soplin", "Tapiche", "Victor Cobeñas"],
    "Ucayali":                ["Contamana", "Inahuaya", "Padre Márquez", "Pampa Hermosa", "Sarayacu", "Vargas Guerra"]
  },
  "Madre de Dios": {
    "Manu":      ["Fitzcarrald", "Huepetuhe", "Madre de Dios", "Manu"],
    "Tahuamanu": ["Iberia", "Iñapari", "Tahuamanu"],
    "Tambopata": ["Inambari", "Las Piedras", "Laberinto", "Puerto Maldonado", "Tambopata"]
  },
  "Moquegua": {
    "General Sánchez Cerro": ["Chojata", "Coalaque", "Ichuña", "La Capilla", "Lloque", "Matalaque", "Omate", "Puquina", "Quinistaquillas", "Ubinas", "Yunga"],
    "Ilo":                   ["El Algarrobal", "Ilo", "Pacocha"],
    "Mariscal Nieto":        ["Carumas", "Cuchumbaya", "Moquegua", "Samegua", "San Cristóbal", "Torata"]
  },
  "Pasco": {
    "Daniel Alcides Carrión": ["Chacayán", "Goyllarisquizga", "Paucar", "San Pedro de Pillao", "Santa Ana de Tusi", "Tapuc", "Vilcabamba", "Yanahuanca"],
    "Oxapampa":               ["Chontabamba", "Huancabamba", "Oxapampa", "Palaz", "Pozuzo", "Puerto Bermúdez", "Villa Rica", "Constitución"],
    "Pasco":                  ["Huachón", "Huariaca", "Huayllay", "Ninacaca", "Pallanchacra", "Paucartambo", "San Francisco de Asís de Yarusyacan", "Santa Ana de Tusi", "Simón Bolívar", "Ticlacayán", "Tinyahuarco", "Vicco", "Yanacancha"]
  },
  "Piura": {
    "Ayabaca":     ["Ayabaca", "Frias", "Jililí", "Lagunas", "Montero", "Pacaipampa", "Paimas", "Sapillica", "Sicchez", "Suyo"],
    "Huancabamba": ["Carmen de la Frontera", "Huancabamba", "Huarmaca", "Lalaquiz", "San Miguel de El Faique", "Sondor", "Sondorillo"],
    "Morropón":    ["Buenos Aires", "Chalaco", "Chulucanas", "La Matanza", "Morropón", "Salitral", "San Juan de Bigote", "Santa Catalina de Mossa", "Santo Domingo", "Yamango"],
    "Paita":       ["Amotape", "Arenal", "Colan", "La Huaca", "Lobitos", "Los Organos", "Paita", "Tamarindo", "Vichayal"],
    "Piura":       ["Castilla", "Catacaos", "Cura Mori", "El Tallán", "La Arena", "La Unión", "Las Lomas", "Piura", "Tambogrande", "Veintiseis de Octubre"],
    "Sechura":     ["Bellavista de la Unión", "Bernal", "Cristo Nos Valga", "Rinconada Llicuar", "Sechura", "Vice"],
    "Sullana":     ["Bellavista", "Ignacio Escudero", "Lancones", "Marcavelica", "Miguel Checa", "Querecotillo", "Salitral", "Sullana"],
    "Talara":      ["El Alto", "La Brea", "Lobitos", "Los Organos", "Máncora", "Pariñas"]
  },
  "Puno": {
    "Azángaro":            ["Achaya", "Arapa", "Asillo", "Azángaro", "Caminaca", "Chupa", "José Domingo Choquehuanca", "Muñani", "Potoni", "Saman", "San Antón", "San José", "San Juan de Salinas", "Santiago de Pupuja", "Tirapata"],
    "Carabaya":            ["Ajoyani", "Ayapata", "Coasa", "Corani", "Crucero", "Ituata", "Macusani", "Ollachea", "San Gabán", "Usicayos"],
    "Chucuito":            ["Desaguadero", "Huacullani", "Juli", "Kelluyo", "Pisacoma", "Pomata", "Zepita"],
    "El Collao":           ["Capazo", "Conduriri", "Ilave", "Pilcuyo", "Santa Rosa"],
    "Huancané":            ["Cojata", "Huancané", "Huatasani", "Inchupalla", "Pusi", "Rosaspata", "Taraco", "Vilque Chico"],
    "Lampa":               ["Cabanilla", "Calapuja", "Lampa", "Nicasio", "Ocuviri", "Palca", "Paratía", "Pucará", "Santa Lucía", "Vilavila"],
    "Melgar":              ["Antauta", "Ayaviri", "Cupi", "Llalli", "Macari", "Nuñoa", "Orurillo", "Santa Rosa", "Umachiri"],
    "Moho":                ["Conima", "Huayrapata", "Moho", "Tilali"],
    "Puno":                ["Acora", "Amantani", "Atuncolla", "Capachica", "Chucuito", "Coata", "Huata", "Mañazo", "Paucarcolla", "Pichacani", "Platería", "Puno", "San Antonio", "Tiquillaca", "Vilque"],
    "San Antonio de Putina":["Ananea", "Pedro Vilca Apaza", "Putina", "Quilcapuncu", "Sina"],
    "San Román":           ["Caracoto", "Cabana", "Juliaca", "San Miguel", "Taraco"],
    "Sandia":              ["Alto Inambari", "Cuyocuyo", "Limbani", "Phara", "Patambuco", "Quiaca", "San Juan del Oro", "Sandia", "Yanahuaya"],
    "Yunguyo":             ["Anapia", "Copani", "Cuturapi", "Ollaraya", "Tinicachi", "Unicachi", "Yunguyo"]
  },
  "San Martín": {
    "Bellavista":     ["Alto Biavo", "Bajo Biavo", "Bellavista", "Huallaga", "Pachiza", "San Pablo"],
    "El Dorado":      ["Agua Blanca", "San José de Sisa", "San Martín", "Santa Rosa", "Shatoja"],
    "Huallaga":       ["Alto Saposoa", "El Eslabón", "Piscoyacu", "Sacanche", "Saposoa", "Tingo de Saposoa"],
    "Lamas":          ["Alonso de Alvarado", "Barranquita", "Caynarachi", "Cuñumbuqui", "Lamas", "Pinto Recodo", "Rumisapa", "San Roque de Cumbaza", "Shanao", "Tabalosos", "Zapatero"],
    "Mariscal Cáceres":["Buenos Aires", "Campanilla", "Huicungo", "Juanjui", "Pachiza", "Pajarillo"],
    "Moyobamba":      ["Calzada", "Habana", "Jepelacio", "Moyobamba", "Soritor", "Yantalo"],
    "Picota":         ["Buenos Aires", "Caspizapa", "Leoncio Prado", "Pilluana", "Pucacaca", "San Cristóbal", "San Hilarión", "Shamboyacu", "Tingo de Ponaza", "Tres Unidos", "Picota"],
    "Rioja":          ["Awajún", "Elías Soplin Vargas", "Nueva Cajamarca", "Pardo Miguel", "Posic", "Rioja", "San Fernando", "Yorongos", "Yuracyacu"],
    "San Martín":     ["Alberto Leveau", "Cacatachi", "Chazuta", "Chipurana", "El Porvenir", "Huimbayoc", "Juan Guerra", "La Banda de Shilcayo", "Morales", "Papaplaya", "San Antonio", "Santa Rosa", "Sauce", "Shapaja", "Tarapoto"],
    "Tocache":        ["Nuevo Progreso", "Pólvora", "Shunte", "Tocache", "Uchiza"]
  },
  "Tacna": {
    "Candarave":    ["Cairani", "Camilaca", "Candarave", "Curibaya", "Huanuara", "Quilahuani"],
    "Jorge Basadre":["Ilabaya", "Ite", "Locumba"],
    "Tacna":        ["Alto de la Alianza", "Calana", "Ciudad Nueva", "Coronel Gregorio Albarracín Lanchipa", "Inclán", "Palca", "Pocollay", "Sama", "Tacna"],
    "Tarata":       ["Chucatamani", "Estique", "Estique-Pampa", "Héroe Albarracín", "Sitajara", "Susapaya", "Tarata", "Tarucachi", "Ticaco"]
  },
  "Tumbes": {
    "Contralmirante Villar": ["Casitas", "Canoas de Punta Sal", "Zorritos"],
    "Tumbes":                ["La Cruz", "Pampas de Hospital", "San Jacinto", "San Juan de la Virgen", "Tumbes"],
    "Zarumilla":             ["Aguas Verdes", "Matapalo", "Papayal", "Zarumilla"]
  },
  "Ucayali": {
    "Atalaya":          ["Raimondi", "Sepahua", "Tahuania", "Yurúa"],
    "Coronel Portillo": ["Callería", "Campo Verde", "Iparía", "Manantay", "Masisea", "Nueva Requena", "Yarinacocha"],
    "Padre Abad":       ["Alexander Von Humboldt", "Curimaná", "Irazola", "Neshuya", "Padre Abad"],
    "Purús":            ["Purús"]
  }
};

/* ─── Helpers ─────────────────────────────────────────────────────────── */

function _clearSelect(sel, placeholder) {
  sel.innerHTML = '<option value="">' + placeholder + '</option>';
  sel.disabled = true;
}

function _fillSelect(sel, items, placeholder) {
  sel.innerHTML = '<option value="">' + placeholder + '</option>';
  items.forEach(function (item) {
    var opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    sel.appendChild(opt);
  });
  sel.disabled = false;
}

/* ─── Bootstrap on load ───────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {
  var deptoSel = document.getElementById('id_departamento');
  var provSel  = document.getElementById('id_provincia');
  var distSel  = document.getElementById('id_distrito');

  if (!deptoSel || !provSel || !distSel) return;

  var initProv = provSel.dataset.initial || '';
  var initDist = distSel.dataset.initial || '';

  /* Restore on re-submission (form has errors, values must be kept) */
  var initDepto = deptoSel.value;
  if (initDepto && PERU_GEO[initDepto]) {
    _fillSelect(provSel, Object.keys(PERU_GEO[initDepto]), 'Seleccione provincia');
    if (initProv && PERU_GEO[initDepto][initProv]) {
      provSel.value = initProv;
      _fillSelect(distSel, PERU_GEO[initDepto][initProv], 'Seleccione distrito');
      if (initDist) distSel.value = initDist;
    }
  }

  /* Departamento change → repopulate provincias, clear distrito */
  deptoSel.addEventListener('change', function () {
    var depto = this.value;
    _clearSelect(provSel, 'Seleccione provincia');
    _clearSelect(distSel, 'Seleccione distrito');
    if (depto && PERU_GEO[depto]) {
      _fillSelect(provSel, Object.keys(PERU_GEO[depto]), 'Seleccione provincia');
    }
  });

  /* Provincia change → repopulate distritos */
  provSel.addEventListener('change', function () {
    var depto = deptoSel.value;
    var prov  = this.value;
    _clearSelect(distSel, 'Seleccione distrito');
    if (depto && prov && PERU_GEO[depto] && PERU_GEO[depto][prov]) {
      _fillSelect(distSel, PERU_GEO[depto][prov], 'Seleccione distrito');
    }
  });
});
