import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# Lägg till 2 timmar för Stockholm sommartid
stockholm_time = datetime.now() + timedelta(hours=2)

def create_complete_dashboard():
    """Skapa en interaktiv HTML-dashboard för alla regeringsdokument"""
    
    # Hämta koder
    codes_response = requests.get('https://g0v.se/api/codes.json')
    all_codes = codes_response.json()
    
    # Hämta alla dokumenttyper
    print("Hämtar dokument...")
    
    # Kommittédirektiv
    kd_response = requests.get('https://g0v.se/rattsliga-dokument/kommittedirektiv.json')
    kd_lista = kd_response.json()
    for doc in kd_lista:
        doc['document_type'] = 'Kommittédirektiv'
    print(f"- {len(kd_lista)} kommittédirektiv")
    
    # Ds och PM
    ds_response = requests.get('https://g0v.se/rattsliga-dokument/departementsserien-och-promemorior.json')
    ds_lista = ds_response.json()
    for doc in ds_lista:
        doc['document_type'] = 'Ds/PM'
    print(f"- {len(ds_lista)} Ds/PM")
    
    # SOU
    sou_response = requests.get('https://g0v.se/rattsliga-dokument/statens-offentliga-utredningar.json')
    sou_lista = sou_response.json()
    for doc in sou_lista:
        doc['document_type'] = 'SOU'
    print(f"- {len(sou_lista)} SOU")
    
    # Regeringsuppdrag
    ru_response = requests.get('https://g0v.se/regeringsuppdrag.json')
    ru_lista = ru_response.json()
    for doc in ru_lista:
        doc['document_type'] = 'Regeringsuppdrag'
    print(f"- {len(ru_lista)} regeringsuppdrag")
    
    # Rapporter
    rap_response = requests.get('https://g0v.se/rapporter.json')
    rap_lista = rap_response.json()
    for doc in rap_lista:
        doc['document_type'] = 'Rapport'
    print(f"- {len(rap_lista)} rapporter")
    
    # Kombinera alla dokument
    alla_dokument = kd_lista + ds_lista + sou_lista + ru_lista + rap_lista
    print(f"\nTotalt: {len(alla_dokument)} dokument")
    
    # Samla alla unika departement och kategorier
    all_departments = set()
    all_categories = set()
    
    # Lista över giltiga departement-suffix och specialfall
    valid_department_endings = [
        'departementet',
        'Statsrådsberedningen',
        'Regeringen',
        'Regeringskansliet'
    ]
    
    for doc in alla_dokument:
        for sender in doc.get('senders', []):
            dept_name = all_codes.get(str(sender), f"Okänt ({sender})")
            
            # Kontrollera om det är ett faktiskt departement
            is_department = any(dept_name.endswith(ending) for ending in valid_department_endings)
            
            if is_department:
                all_departments.add((str(sender), dept_name))
        
        for category in doc.get('categories', []):
            cat_name = all_codes.get(str(category), f"Okänd ({category})")
            all_categories.add((str(category), cat_name))
    
    sorted_departments = sorted(all_departments, key=lambda x: x[1])
    sorted_categories = sorted(all_categories, key=lambda x: x[1])
    
    # Skapa HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <title>Regeringens dokument - Komplett Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1600px;
                margin: 0 auto;
            }}
            .header {{
                background-color: #1a5490;
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .filters {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .filter-section {{
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-height: 400px;
                overflow-y: auto;
            }}
            .filter-section h3 {{
                margin-top: 0;
                color: #1a5490;
                position: sticky;
                top: 0;
                background: white;
                padding-bottom: 10px;
                border-bottom: 2px solid #1a5490;
            }}
            .checkbox-item {{
                margin: 5px 0;
                padding: 5px;
            }}
            .checkbox-item:hover {{
                background-color: #f0f0f0;
            }}
            .results {{
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .document-item {{
                border-bottom: 1px solid #eee;
                padding: 15px 0;
            }}
            .document-item:last-child {{
                border-bottom: none;
            }}
            .document-title {{
                font-weight: bold;
                color: #1a5490;
                margin-bottom: 5px;
                font-size: 1.1em;
            }}
            .document-meta {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }}
            .document-summary {{
                margin-top: 10px;
                line-height: 1.5;
            }}
            .control-buttons {{
                margin: 20px 0;
                text-align: center;
            }}
            button {{
                background-color: #1a5490;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 0 5px;
                border-radius: 3px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #2a6bb0;
            }}
            .result-count {{
                font-weight: bold;
                color: #1a5490;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            input[type="checkbox"] {{
                margin-right: 8px;
            }}
            .doc-type-badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 0.85em;
                font-weight: bold;
                margin-right: 10px;
            }}
            .badge-kd {{ background-color: #e3f2fd; color: #1565c0; }}
            .badge-ds {{ background-color: #f3e5f5; color: #6a1b9a; }}
            .badge-sou {{ background-color: #e8f5e9; color: #2e7d32; }}
            .badge-ru {{ background-color: #fff3e0; color: #e65100; }}
            .badge-rap {{ background-color: #fce4ec; color: #c2185b; }}
            #searchBox {{
                width: 100%;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 3px;
                margin-bottom: 20px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }}
            .stat-box {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 1.8em;
                font-weight: bold;
                color: #1a5490;
            }}
            .stat-label {{
                color: #666;
                font-size: 0.85em;
            }}
            @media (max-width: 1200px) {{
                .stats {{ grid-template-columns: repeat(3, 1fr); }}
            }}
            @media (max-width: 768px) {{
                .filters {{ grid-template-columns: 1fr; }}
                .stats {{ grid-template-columns: repeat(2, 1fr); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Regeringens dokument</h1>
                <p>Sök och filtrera bland regeringsdokument</p>
                <p>Senast uppdaterad: {stockholm_time.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-box">
                    <div class="stat-number">{len(alla_dokument)}</div>
                    <div class="stat-label">Totalt</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(kd_lista)}</div>
                    <div class="stat-label">Kommittédirektiv</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(ds_lista)}</div>
                    <div class="stat-label">Ds/PM</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(sou_lista)}</div>
                    <div class="stat-label">SOU</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(ru_lista)}</div>
                    <div class="stat-label">Regeringsuppdrag</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(rap_lista)}</div>
                    <div class="stat-label">Rapporter</div>
                </div>
            </div>
            
            <div class="control-buttons">
                <button onclick="clearAllFilters()">Rensa alla filter</button>
                <button onclick="selectAllDocTypes()">Välj alla dokumenttyper</button>
                <button onclick="selectAllDepartments()">Välj alla departement</button>
                <button onclick="selectAllCategories()">Välj alla kategorier</button>
                <button onclick="exportResults()">Exportera resultat (CSV)</button>
            </div>
            
            <div class="filters">
                <div class="filter-section">
                    <h3>Dokumenttyp</h3>
                    <div id="doctypes">
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="doctype-filter" value="Kommittédirektiv" onchange="filterDocuments()" checked>
                                Kommittédirektiv ({len(kd_lista)})
                            </label>
                        </div>
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="doctype-filter" value="Ds/PM" onchange="filterDocuments()" checked>
                                Ds/PM ({len(ds_lista)})
                            </label>
                        </div>
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="doctype-filter" value="SOU" onchange="filterDocuments()" checked>
                                SOU ({len(sou_lista)})
                            </label>
                        </div>
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="doctype-filter" value="Regeringsuppdrag" onchange="filterDocuments()" checked>
                                Regeringsuppdrag ({len(ru_lista)})
                            </label>
                        </div>
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="doctype-filter" value="Rapport" onchange="filterDocuments()" checked>
                                Rapporter ({len(rap_lista)})
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="filter-section">
                    <h3>Departement ({len(sorted_departments)} st)</h3>
                    <div id="departments">
    """
    
    # Lägg till departement-checkboxar
    for dept_id, dept_name in sorted_departments:
        html_content += f"""
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="dept-filter" value="{dept_id}" onchange="filterDocuments()">
                                {dept_name}
                            </label>
                        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
                
                <div class="filter-section">
                    <h3>Kategorier ({len(sorted_categories)} st)</h3>
                    <div id="categories">
    """
    
    # Lägg till kategori-checkboxar
    for cat_id, cat_name in sorted_categories:
        html_content += f"""
                        <div class="checkbox-item">
                            <label>
                                <input type="checkbox" class="cat-filter" value="{cat_id}" onchange="filterDocuments()">
                                {cat_name}
                            </label>
                        </div>
        """
    
    html_content += """
                    </div>
                </div>
            </div>
            
            <div class="results">
                <input type="text" id="searchBox" placeholder="Sök i titlar, sammanfattningar och ID..." onkeyup="filterDocuments()">
                <div class="result-count" id="resultCount">Visar alla dokument</div>
                <div id="document-list"></div>
            </div>
        </div>
        
        <script>
            // Lagra all dokument-data
            const allDocuments = """ + json.dumps(alla_dokument, ensure_ascii=False) + """;
            const allCodes = """ + json.dumps(all_codes, ensure_ascii=False) + """;
            let currentFilteredDocuments = [];
            
            // Initial visning
            window.onload = function() {
                filterDocuments();
            };
            
            function filterDocuments() {
                // Hämta valda filter
                const selectedDocTypes = Array.from(document.querySelectorAll('.doctype-filter:checked')).map(cb => cb.value);
                const selectedDepts = Array.from(document.querySelectorAll('.dept-filter:checked')).map(cb => cb.value);
                const selectedCats = Array.from(document.querySelectorAll('.cat-filter:checked')).map(cb => cb.value);
                const searchTerm = document.getElementById('searchBox').value.toLowerCase();
                
                // Filtrera dokument
                currentFilteredDocuments = allDocuments.filter(doc => {
                    // Kontrollera dokumenttyp
                    if (!selectedDocTypes.includes(doc.document_type)) {
                        return false;
                    }
                    
                    // Kontrollera departement (om några valda)
                    if (selectedDepts.length > 0) {
                        const deptMatch = doc.senders && doc.senders.some(sender => selectedDepts.includes(String(sender)));
                        if (!deptMatch) return false;
                    }
                    
                    // Kontrollera kategorier (om några valda)
                    if (selectedCats.length > 0) {
                        const catMatch = doc.categories && doc.categories.some(cat => selectedCats.includes(String(cat)));
                        if (!catMatch) return false;
                    }
                    
                    // Kontrollera sökterm
                    if (searchTerm) {
                        const searchableText = (
                            (doc.title || '') + ' ' + 
                            (doc.summary || '') + ' ' +
                            (doc.id || '')
                        ).toLowerCase();
                        if (!searchableText.includes(searchTerm)) return false;
                    }
                    
                    return true;
                });
                
                // Sortera efter publiceringsdatum (nyast först)
                currentFilteredDocuments.sort((a, b) => {
                    const dateA = new Date(a.published || '1900-01-01');
                    const dateB = new Date(b.published || '1900-01-01');
                    return dateB - dateA;
                });
                
                // Uppdatera resultaträknare
                document.getElementById('resultCount').textContent = 
                    `Visar ${currentFilteredDocuments.length} av ${allDocuments.length} dokument`;
                
                // Visa dokument
                const listElement = document.getElementById('document-list');
                listElement.innerHTML = '';
                
                // Begränsa till 500 dokument för prestanda
                const documentsToShow = currentFilteredDocuments.slice(0, 500);
                
                documentsToShow.forEach(doc => {
                    const docElement = document.createElement('div');
                    docElement.className = 'document-item';
                    
                    // Hämta departementnamn
                    const deptNames = (doc.senders || []).map(s => 
                        allCodes[String(s)] || `Okänt (${s})`
                    ).join(', ');
                    
                    // Hämta kategorinamn
                    const catNames = (doc.categories || []).map(c => 
                        allCodes[String(c)] || `Okänd (${c})`
                    ).join(', ');
                    
                    // Badge-klass baserat på dokumenttyp
                    let badgeClass = 'doc-type-badge ';
                    if (doc.document_type === 'Kommittédirektiv') badgeClass += 'badge-kd';
                    else if (doc.document_type === 'Ds/PM') badgeClass += 'badge-ds';
                    else if (doc.document_type === 'SOU') badgeClass += 'badge-sou';
                    else if (doc.document_type === 'Regeringsuppdrag') badgeClass += 'badge-ru';
                    else if (doc.document_type === 'Rapport') badgeClass += 'badge-rap';
                    
                    docElement.innerHTML = `
                        <div class="document-title">
                            <span class="${badgeClass}">${doc.document_type}</span>
                            ${doc.title || 'Ingen titel'}
                        </div>
                        <div class="document-meta">
                            <strong>ID:</strong> ${doc.id || 'Inget ID'} | 
                            <strong>Publicerad:</strong> ${doc.published || 'Okänt datum'}
                            ${deptNames ? ` | <strong>Departement:</strong> ${deptNames}` : ''}
                            ${catNames ? ` | <strong>Kategorier:</strong> ${catNames}` : ''}
                        </div>
                        ${doc.summary ? `<div class="document-summary">${doc.summary}</div>` : ''}
                        ${doc.url ? `<div style="margin-top: 10px;"><a href="https://www.regeringen.se${doc.url}" target="_blank">Läs mer →</a></div>` : ''}
                    `;
                    
                    listElement.appendChild(docElement);
                });
                
                if (currentFilteredDocuments.length === 0) {
                    listElement.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Inga dokument matchar de valda filtren.</p>';
                } else if (currentFilteredDocuments.length > 500) {
                    listElement.innerHTML += '<p style="text-align: center; color: #666; padding: 20px;"><strong>Visar de 500 senaste dokumenten.</strong> Förfina din sökning för att se fler resultat.</p>';
                }
                
                // Uppdatera statistik
                updateStatistics(currentFilteredDocuments);
            }
            
            function updateStatistics(documents) {
                const kdCount = documents.filter(d => d.document_type === 'Kommittédirektiv').length;
                const dsCount = documents.filter(d => d.document_type === 'Ds/PM').length;
                const souCount = documents.filter(d => d.document_type === 'SOU').length;
                const ruCount = documents.filter(d => d.document_type === 'Regeringsuppdrag').length;
                const rapCount = documents.filter(d => d.document_type === 'Rapport').length;
                
                document.getElementById('stats').innerHTML = `
                    <div class="stat-box">
                        <div class="stat-number">${documents.length}</div>
                        <div class="stat-label">Filtrerade</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${kdCount}</div>
                        <div class="stat-label">Kommittédirektiv</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${dsCount}</div>
                        <div class="stat-label">Ds/PM</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${souCount}</div>
                        <div class="stat-label">SOU</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${ruCount}</div>
                        <div class="stat-label">Regeringsuppdrag</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">${rapCount}</div>
                        <div class="stat-label">Rapporter</div>
                    </div>
                `;
            }
            
            function clearAllFilters() {
                document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
                document.getElementById('searchBox').value = '';
                // Behåll dokumenttyper markerade
                document.querySelectorAll('.doctype-filter').forEach(cb => cb.checked = true);
                filterDocuments();
            }
            
            function selectAllDocTypes() {
                document.querySelectorAll('.doctype-filter').forEach(cb => cb.checked = true);
                filterDocuments();
            }
            
            function selectAllDepartments() {
                document.querySelectorAll('.dept-filter').forEach(cb => cb.checked = true);
                filterDocuments();
            }
            
            function selectAllCategories() {
                document.querySelectorAll('.cat-filter').forEach(cb => cb.checked = true);
                filterDocuments();
            }
            
            function exportResults() {
                if (currentFilteredDocuments.length === 0) {
                    alert('Inga dokument att exportera!');
                    return;
                }
                
                // Lägg till BOM för UTF-8 så Excel förstår kodningen
                const BOM = '\\ufeff';
                
                // Skapa CSV-innehåll med semikolon som separator
                let csv = BOM + 'Dokumenttyp;ID;Titel;Publicerad;Departement;Kategorier;URL\\n';
                
                currentFilteredDocuments.forEach(doc => {
                    const deptNames = (doc.senders || []).map(s => 
                        allCodes[String(s)] || `Okänt (${s})`
                    ).join(', ');
                    
                    const catNames = (doc.categories || []).map(c => 
                        allCodes[String(c)] || `Okänd (${c})`
                    ).join(', ');
                    
                    const row = [
                        doc.document_type,
                        doc.id || '',
                        `"${(doc.title || '').replace(/"/g, '""')}"`,
                        doc.published || '',
                        `"${deptNames.replace(/"/g, '""')}"`,
                        `"${catNames.replace(/"/g, '""')}"`,
                        doc.url ? `https://www.regeringen.se${doc.url}` : ''
                    ].join(';');
                    
                    csv += row + '\\n';
                });
                
                // Skapa och ladda ner fil
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `regeringsdokument_${new Date().toISOString().slice(0,10)}.csv`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            // Lägg till kortkommandon
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K för att fokusera på sökrutan
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    document.getElementById('searchBox').focus();
                }
                // Escape för att rensa sökning
                if (e.key === 'Escape') {
                    document.getElementById('searchBox').value = '';
                    filterDocuments();
                }
            });
        </script>
    </body>
    </html>
    """
    
    # Spara HTML-filen
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\nKomplett dashboard skapad: index.html")
    print("\nStatistik:")
    print(f"- Totalt antal dokument: {len(alla_dokument)}")
    print(f"  - Kommittédirektiv: {len(kd_lista)}")
    print(f"  - Ds/PM: {len(ds_lista)}")
    print(f"  - SOU: {len(sou_lista)}")
    print(f"  - Regeringsuppdrag: {len(ru_lista)}")
    print(f"  - Rapporter: {len(rap_lista)}")
    print(f"- Antal departement: {len(sorted_departments)}")
    print(f"- Antal kategorier: {len(sorted_categories)}")
    
    # Visa årsfördelning
    years_count = defaultdict(int)
    for doc in alla_dokument:
        if doc.get('published'):
            try:
                year = doc['published'][:4]
                years_count[year] += 1
            except:
                pass
    
    print("\nDokument per år (senaste 5 åren):")
    for year in sorted(years_count.keys(), reverse=True)[:5]:
        print(f"- {year}: {years_count[year]} dokument")
    
    # Visa vanligaste kategorierna
    cat_count = defaultdict(int)
    for doc in alla_dokument:
        for cat in doc.get('categories', []):
            cat_name = all_codes.get(str(cat), f"Okänd ({cat})")
            cat_count[cat_name] += 1
    
    print("\nVanligaste kategorierna:")
    for cat, count in sorted(cat_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {cat}: {count} dokument")

# Skapa även en funktion för att söka specifikt innehåll
def search_documents(search_term, doc_types=None, departments=None, categories=None):
    """Sök dokument baserat på kriterier"""
    
    # Hämta koder
    codes_response = requests.get('https://g0v.se/api/codes.json')
    all_codes = codes_response.json()
    
    # Lista med alla API:er
    apis = [
        ('Kommittédirektiv', 'https://g0v.se/rattsliga-dokument/kommittedirektiv.json'),
        ('Ds/PM', 'https://g0v.se/rattsliga-dokument/departementsserien-och-promemorior.json'),
        ('SOU', 'https://g0v.se/rattsliga-dokument/statens-offentliga-utredningar.json'),
        ('Regeringsuppdrag', 'https://g0v.se/regeringsuppdrag.json'),
        ('Rapport', 'https://g0v.se/rapporter.json')
    ]
    
    results = []
    
    for doc_type, api_url in apis:
        # Hoppa över om specifika dokumenttyper är valda
        if doc_types and doc_type not in doc_types:
            continue
            
        response = requests.get(api_url)
        documents = response.json()
        
        for doc in documents:
            # Säkerställ att alla värden är strängar (konvertera None till '')
            title = str(doc.get('title') or '')
            summary = str(doc.get('summary') or '')
            doc_id = str(doc.get('id') or '')
            
            # Sök i text
            searchable_text = (title + ' ' + summary + ' ' + doc_id).lower()
            
            if search_term.lower() not in searchable_text:
                continue
            
            # Filtrera på departement om angivet
            if departments:
                dept_match = False
                for sender in doc.get('senders', []):
                    dept_name = all_codes.get(str(sender), '')
                    if any(dept.lower() in dept_name.lower() for dept in departments):
                        dept_match = True
                        break
                if not dept_match:
                    continue
            
            # Filtrera på kategorier om angivet
            if categories:
                cat_match = False
                for cat in doc.get('categories', []):
                    cat_name = all_codes.get(str(cat), '')
                    if any(category.lower() in cat_name.lower() for category in categories):
                        cat_match = True
                        break
                if not cat_match:
                    continue
            
            # Lägg till dokumenttyp och resultat
            doc['document_type'] = doc_type
            results.append(doc)
    
    return results

# Exempel på användning
if __name__ == "__main__":
    # Skapa komplett dashboard
    create_complete_dashboard()
