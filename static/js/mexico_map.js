// Mexico Map Renderer - Real GeoJSON with Mercator projection
const MEXICO_GEOJSON_URL='https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json';
let mexicoGeoData=null;

// Approximate distances (km) between major Mexican cities for time estimation
const DISTANCE_TABLE={
"Orizaba-Guanajuato":520,"Guanajuato-Orizaba":520,
"Orizaba-Xalapa":120,"Xalapa-Orizaba":120,
"CDMX-Monterrey":900,"Monterrey-CDMX":900,
"CDMX-Guadalajara":540,"Guadalajara-CDMX":540,
"CDMX-Puebla":130,"Puebla-CDMX":130,
"CDMX-Querétaro":220,"Querétaro-CDMX":220,
"CDMX-Guanajuato":370,"Guanajuato-CDMX":370,
"CDMX-Veracruz":420,"Veracruz-CDMX":420,
"CDMX-Oaxaca":460,"Oaxaca-CDMX":460,
"Monterrey-Guadalajara":780,"Guadalajara-Monterrey":780,
"Guadalajara-Guanajuato":280,"Guanajuato-Guadalajara":280,
"Puebla-Veracruz":290,"Veracruz-Puebla":290,
"CDMX-Mérida":1300,"Mérida-CDMX":1300,
"CDMX-Cancún":1700,"Cancún-CDMX":1700,
"CDMX-Chihuahua":1400,"Chihuahua-CDMX":1400,
"CDMX-Tijuana":2800,"Tijuana-CDMX":2800,
"Monterrey-Saltillo":90,"Saltillo-Monterrey":90,
"Guadalajara-Colima":200,"Colima-Guadalajara":200,
"Orizaba-Guanajujato":520,"Guanajujato-Orizaba":520,
};

// City coordinates (lon, lat)
const CITY_COORDS={
"Ciudad de México":[-99.13,19.43],"CDMX":[-99.13,19.43],"México":[-99.13,19.43],
"Guadalajara":[-103.35,20.67],"Jalisco":[-103.35,20.67],
"Monterrey":[-100.31,25.67],"Nuevo León":[-100.31,25.67],
"Guanajuato":[-101.26,21.02],"León":[-101.68,21.12],"Guanajujato":[-101.26,21.02],
"Querétaro":[-100.39,20.59],"Puebla":[-98.21,19.04],
"Aguascalientes":[-102.29,21.88],"San Luis Potosí":[-100.99,22.15],
"Chihuahua":[-106.09,28.63],"Tijuana":[-117.02,32.53],
"Baja California":[-117.02,32.53],"Hermosillo":[-110.97,29.07],"Sonora":[-110.97,29.07],
"Mérida":[-89.62,20.97],"Yucatán":[-89.62,20.97],
"Cancún":[-86.85,21.17],"Quintana Roo":[-86.85,21.17],
"Veracruz":[-96.13,19.17],"Xalapa":[-96.92,19.54],
"Oaxaca":[-96.73,17.07],"Tabasco":[-92.95,17.99],"Villahermosa":[-92.95,17.99],
"Chiapas":[-93.11,16.75],"Tuxtla Gutiérrez":[-93.11,16.75],
"Morelia":[-101.19,19.70],"Michoacán":[-101.19,19.70],
"Toluca":[-99.66,19.29],"Estado de México":[-99.66,19.29],"Edo. de México":[-99.66,19.29],
"Zacatecas":[-102.56,22.77],"Durango":[-104.67,24.02],
"Tampico":[-97.86,22.23],"Tamaulipas":[-97.86,22.23],
"Mazatlán":[-106.42,23.24],"Sinaloa":[-107.39,24.81],"Culiacán":[-107.39,24.81],
"Colima":[-103.72,19.24],"Nayarit":[-104.89,21.50],"Tepic":[-104.89,21.50],
"Coahuila":[-101.42,25.42],"Saltillo":[-100.99,25.42],
"Campeche":[-90.53,19.84],"Guerrero":[-99.50,17.55],"Acapulco":[-99.91,16.86],
"Tlaxcala":[-98.24,19.32],"Hidalgo":[-98.76,20.12],"Pachuca":[-98.73,20.12],
"Baja California Sur":[-112.00,24.14],"La Paz":[-110.31,24.14],
"Orizaba":[-97.10,18.85],"Reynosa":[-98.28,26.09],"Torreón":[-103.44,25.54],
"Irapuato":[-101.35,20.68],"Celaya":[-100.82,20.53],"Salamanca":[-101.19,20.57],
"Silao":[-101.43,20.95],"Zapopan":[-103.40,20.72],"Tlaquepaque":[-103.31,20.64]
};

function projectMerc(lon,lat,w,h){
    const minLon=-118.5,maxLon=-86,minLat=14.5,maxLat=33;
    const x=((lon-minLon)/(maxLon-minLon))*w;
    const latRad=lat*Math.PI/180;
    const mercN=Math.log(Math.tan(Math.PI/4+latRad/2));
    const minLatRad=minLat*Math.PI/180;
    const maxLatRad=maxLat*Math.PI/180;
    const minMerc=Math.log(Math.tan(Math.PI/4+minLatRad/2));
    const maxMerc=Math.log(Math.tan(Math.PI/4+maxLatRad/2));
    const y=h-((mercN-minMerc)/(maxMerc-minMerc))*h;
    return[x,y];
}

function polyToPath(coords,w,h){
    let d='';
    coords.forEach((ring,ri)=>{
        ring.forEach((pt,i)=>{
            const[x,y]=projectMerc(pt[0],pt[1],w,h);
            d+=(i===0?'M':'L')+x.toFixed(1)+','+y.toFixed(1);
        });
        d+='Z ';
    });
    return d;
}

async function loadMexicoMap(){
    if(!mexicoGeoData){
        try{
            const r=await fetch(MEXICO_GEOJSON_URL);
            mexicoGeoData=await r.json();
        }catch(e){console.error('Map load failed',e);return;}
    }
}

function findCityCoord(place){
    if(!place)return null;
    const pl=place.toLowerCase();
    for(const[k,v] of Object.entries(CITY_COORDS)){
        if(pl.includes(k.toLowerCase()))return v;
    }
    for(const[k,v] of Object.entries(CITY_COORDS)){
        if(k.toLowerCase().includes(pl.split(',')[0].trim().toLowerCase()))return v;
    }
    return null;
}

function estimateTime(origin,destination){
    // Try direct lookup
    for(const[k,v] of Object.entries(DISTANCE_TABLE)){
        const parts=k.split('-');
        if(origin.toLowerCase().includes(parts[0].toLowerCase())&&
           destination.toLowerCase().includes(parts[1].toLowerCase())){
            const hrs=v/80; // avg 80km/h for trucks
            return{km:v,hrs:Math.round(hrs*10)/10,text:`~${Math.floor(hrs)}h ${Math.round((hrs%1)*60)}min`};
        }
    }
    // Fallback: estimate from coordinates
    const oC=findCityCoord(origin),dC=findCityCoord(destination);
    if(oC&&dC){
        const R=6371;
        const dLat=(dC[1]-oC[1])*Math.PI/180;
        const dLon=(dC[0]-oC[0])*Math.PI/180;
        const a=Math.sin(dLat/2)**2+Math.cos(oC[1]*Math.PI/180)*Math.cos(dC[1]*Math.PI/180)*Math.sin(dLon/2)**2;
        const dist=R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))*1.3; // 1.3x for road factor
        const hrs=dist/80;
        return{km:Math.round(dist),hrs:Math.round(hrs*10)/10,text:`~${Math.floor(hrs)}h ${Math.round((hrs%1)*60)}min`};
    }
    return null;
}

function renderMexicoMap(svgEl,services){
    if(!mexicoGeoData)return;
    const W=900,H=520;
    svgEl.setAttribute('viewBox',`0 0 ${W} ${H}`);
    let html='';

    // Draw states
    mexicoGeoData.features.forEach(f=>{
        const geo=f.geometry;
        let pathD='';
        if(geo.type==='Polygon'){
            pathD=polyToPath(geo.coordinates,W,H);
        }else if(geo.type==='MultiPolygon'){
            geo.coordinates.forEach(poly=>{pathD+=polyToPath(poly,W,H);});
        }
        html+=`<path class="mexico-state" d="${pathD}" data-name="${f.properties.name}" onclick="onMapBackgroundClick(event)"><title>${f.properties.name}</title></path>`;
    });

    // Draw routes (each wrapped in a group for filtering)
    const routeColors=['#4285F4','#EA4335','#FBBC04','#34A853','#FF6D01','#46BDC6','#7B61FF'];
    let colorIdx=0;
    
    // Track occurrences to offset overlapping routes
    const routeOccurrences = {};

    services.forEach(s=>{
        const oC=findCityCoord(s.origin),dC=findCityCoord(s.destination);
        if(!oC||!dC)return;
        const[ox,oy]=projectMerc(oC[0],oC[1],W,H);
        const[dx,dy]=projectMerc(dC[0],dC[1],W,H);
        
        const pathKey = `${Math.round(ox)},${Math.round(oy)}-${Math.round(dx)},${Math.round(dy)}`;
        if (!routeOccurrences[pathKey]) routeOccurrences[pathKey] = 0;
        const overlapIndex = routeOccurrences[pathKey];
        routeOccurrences[pathKey]++;

        const isActive=!s.arrival_time;
        const color=routeColors[colorIdx%routeColors.length];
        colorIdx++;

        // Calculate perpendicular offset for overlapping routes
        let spreadOffset = 0;
        if (overlapIndex > 0) {
            spreadOffset = Math.ceil(overlapIndex / 2) * 45 * (overlapIndex % 2 === 0 ? -1 : 1);
        }
        let Nx = -(dy - oy);
        let Ny = (dx - ox);
        const len = Math.sqrt(Nx*Nx + Ny*Ny) || 1;
        Nx /= len; Ny /= len;

        const mx = (ox+dx)/2 + Nx * spreadOffset;
        const my = (oy+dy)/2 + Ny * spreadOffset - Math.abs(ox-dx)*0.2 - 30;
        
        const lineClass=isActive?'route-line':'route-line completed';

        // Open group
        html+=`<g class="route-group" data-sid="${s.id}" data-active="${isActive}" data-start="${s.start_time}" onclick="onRouteClick('${s.id}')">`;

        // Shadow
        html+=`<path d="M${ox},${oy} Q${mx},${my} ${dx},${dy}" stroke="rgba(0,0,0,0.3)" stroke-width="5" fill="none" stroke-linecap="round"/>`;
        // Main line
        html+=`<path class="${lineClass}" d="M${ox},${oy} Q${mx},${my} ${dx},${dy}" style="stroke:${color};stroke-width:3.5;stroke-linecap:round;" data-sid="${s.id}" data-unit="${s.unit}" data-origin="${s.origin}" data-dest="${s.destination}" data-start="${s.start_time}" data-arrival="${s.arrival_time||''}" data-mins="${s.billed_minutes||''}"/>`;
        // Origin dot
        html+=`<circle cx="${ox}" cy="${oy}" r="5" fill="${color}" stroke="#fff" stroke-width="1.5" filter="drop-shadow(0 0 3px ${color})"/>`;
        // Destination dot
        html+=`<circle cx="${dx}" cy="${dy}" r="5" fill="${isActive?'#FBBC04':color}" stroke="#fff" stroke-width="1.5" filter="drop-shadow(0 0 3px ${isActive?'#FBBC04':color})"/>`;

        // Floating label
        const est=estimateTime(s.origin,s.destination);
        // Position label at the Bezier curve midpoint (t=0.5)
        const bx = 0.25 * ox + 0.5 * mx + 0.25 * dx;
        const by = 0.25 * oy + 0.5 * my + 0.25 * dy;
        const lx = bx, ly = by - 12;
        if(isActive){
            const start=parseServiceDateMap(s.start_time);
            let elapsed='';
            if(start){
                const diff=Date.now()-start.getTime();
                const h=Math.floor(diff/3600000),m=Math.floor((diff%3600000)/60000);
                elapsed=`${h}h ${m}m`;
            }
            html+=`<g class="route-label" transform="translate(${lx},${ly})">
                <rect x="-50" y="-16" width="100" height="32" rx="6" fill="${color}" opacity="0.95" filter="drop-shadow(0 2px 6px rgba(0,0,0,0.4))"/>
                <text x="0" y="-2" text-anchor="middle" fill="#fff" font-size="9" font-weight="700" font-family="Inter,sans-serif">🚛 ${s.unit}</text>
                <text x="0" y="10" text-anchor="middle" fill="#fff" font-size="8" font-family="Inter,sans-serif">${elapsed?'⏱ '+elapsed:''}${est?' · '+est.text:''}</text>
            </g>`;
        }else if(est){
            html+=`<g class="route-label" transform="translate(${lx},${ly})">
                <rect x="-40" y="-10" width="80" height="20" rx="5" fill="rgba(30,41,59,0.9)" stroke="rgba(255,255,255,0.15)" stroke-width="0.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.3))"/>
                <text x="0" y="4" text-anchor="middle" fill="#94a3b8" font-size="8" font-family="Inter,sans-serif">✅ ${est.text} · ${est.km}km</text>
            </g>`;
        }

        html+=`</g>`; // Close group
    });

    svgEl.innerHTML=html;

    // Add hover interaction for route lines
    const tooltip=document.getElementById('routeTooltip');
    svgEl.querySelectorAll('.route-line').forEach(path=>{
        path.addEventListener('mouseenter',e=>{
            const d=path.dataset;
            const isActive=!d.arrival;
            let h=`<div class="tt-unit">🚛 ${d.unit}</div><div class="tt-route">${d.origin} → ${d.dest}</div>`;
            if(isActive){
                const start=parseServiceDateMap(d.start);
                if(start){
                    const diff=Date.now()-start.getTime();
                    const hrs=Math.floor(diff/3600000),mins=Math.floor((diff%3600000)/60000);
                    h+=`<div class="tt-time">⏱️ ${hrs}h ${mins}m en ruta</div>`;
                }
                const est=estimateTime(d.origin,d.dest);
                if(est)h+=`<div style="color:#94a3b8;font-size:11px;">📍 Distancia est: ${est.km}km · ${est.text}</div>`;
            }else{
                h+=`<div style="color:#10b981;">✅ Completado — ${d.mins||0} mins</div>`;
            }
            tooltip.innerHTML=h;tooltip.style.display='block';
        });
        path.addEventListener('mousemove',e=>{tooltip.style.left=(e.clientX+15)+'px';tooltip.style.top=(e.clientY-10)+'px';});
        path.addEventListener('mouseleave',()=>{tooltip.style.display='none';});
    });
}

function parseServiceDateMap(str){
    if(!str)return null;
    const m=str.match(/(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})\s+(AM|PM)/i);
    if(!m)return null;
    let h=parseInt(m[4]);const ampm=m[6].toUpperCase();
    if(ampm==='PM'&&h<12)h+=12;if(ampm==='AM'&&h===12)h=0;
    return new Date(parseInt(m[3]),parseInt(m[2])-1,parseInt(m[1]),h,parseInt(m[5]));
}
