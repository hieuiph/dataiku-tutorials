# ==================== LAYOUT ====================

app.layout = html.Div(
    style={
        'maxWidth': '900px',
        'margin': '40px auto',
        'padding': '0 20px',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'color': '#000',
        'backgroundColor': '#fff'
    },
    children=[
        # Header
        html.H1(
            "JSON Parameter Editor",
            style={
                'textAlign': 'center',
                'fontWeight': '400',
                'fontSize': '24px',
                'marginBottom': '30px',
                'borderBottom': '1px solid #000',
                'paddingBottom': '15px'
            }
        ),
        
        # File Selector Row
        html.Div(
            style={
                'display': 'flex',
                'gap': '10px',
                'marginBottom': '10px'
            },
            children=[
                dcc.Dropdown(
                    id='file-dropdown',
                    placeholder="Select a JSON file...",
                    clearable=False,
                    style={'flex': '1', 'minWidth': '0'}
                ),
                html.Button(
                    "Refresh",
                    id='refresh-btn',
                    n_clicks=0,
                    style={
                        'padding': '0 20px',
                        'height': '36px',
                        'border': '1px solid #000',
                        'borderRadius': '4px',
                        'backgroundColor': '#fff',
                        'color': '#000',
                        'cursor': 'pointer',
                        'fontWeight': '500',
                        'whiteSpace': 'nowrap'
                    }
                )
            ]
        ),
        
        # Status Message
        html.Div(
            id='status-msg',
            style={
                'fontSize': '13px',
                'color': '#666',
                'marginBottom': '15px',
                'minHeight': '20px'
            }
        ),
        
        # JSON Editor
        dcc.Textarea(
            id='json-editor',
            placeholder='Select a file to load its contents...',
            spellCheck=False,
            style={
                'width': '100%',
                'height': '500px',
                'padding': '15px',
                'boxSizing': 'border-box',
                'border': '1px solid #000',
                'borderRadius': '4px',
                'fontFamily': 'Consolas, Monaco, "Courier New", monospace',
                'fontSize': '13px',
                'lineHeight': '1.5',
                'resize': 'vertical',
                'backgroundColor': '#fff'
            }
        ),
        
        # Action Buttons Row
        html.Div(
            style={
                'display': 'flex',
                'gap': '10px',
                'marginTop': '15px'
            },
            children=[
                html.Button(
                    "Format",
                    id='format-btn',
                    n_clicks=0,
                    style={
                        'flex': '1',
                        'height': '44px',
                        'border': '1px solid #000',
                        'borderRadius': '4px',
                        'backgroundColor': '#fff',
                        'color': '#000',
                        'cursor': 'pointer',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }
                ),
                html.Button(
                    "Reload",
                    id='reload-btn',
                    n_clicks=0,
                    style={
                        'flex': '1',
                        'height': '44px',
                        'border': '1px solid #000',
                        'borderRadius': '4px',
                        'backgroundColor': '#fff',
                        'color': '#000',
                        'cursor': 'pointer',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }
                )
            ]
        ),
        
        # Save Button (Full Width)
        html.Button(
            "Save as New Version",
            id='save-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'height': '50px',
                'marginTop': '10px',
                'border': '1px solid #000',
                'borderRadius': '4px',
                'backgroundColor': '#000',
                'color': '#fff',
                'cursor': 'pointer',
                'fontWeight': '600',
                'fontSize': '16px'
            }
        ),
        
        # Result Message Area
        html.Div(
            id='result-msg',
            style={
                'marginTop': '20px',
                'padding': '15px',
                'textAlign': 'center',
                'minHeight': '50px'
            }
        ),
        
        # Hidden Stores
        dcc.Store(id='original-json-store'),
        dcc.Store(id='current-filename-store'),
        dcc.Store(id='refresh-trigger')
    ]
)


# ==================== CALLBACKS ====================

@callback(
    Output('file-dropdown', 'options'),
    Input('refresh-btn', 'n_clicks'),
    Input('refresh-trigger', 'data')
)
def populate_file_list(n_clicks, trigger):
    """Populate dropdown with JSON files."""
    files = list_json_files()
    return [{'label': f, 'value': f} for f in files]


@callback(
    Output('json-editor', 'value'),
    Output('original-json-store', 'data'),
    Output('current-filename-store', 'data'),
    Output('status-msg', 'children'),
    Input('file-dropdown', 'value'),
    Input('reload-btn', 'n_clicks'),
    State('current-filename-store', 'data'),
    prevent_initial_call=True
)
def load_selected_file(selected_file, reload_clicks, stored_filename):
    """Load JSON file content into editor."""
    from dash import ctx
    
    if ctx.triggered_id == 'reload-btn':
        filename = stored_filename
    else:
        filename = selected_file
    
    if not filename:
        return "", None, None, "Select a file to begin editing."
    
    data, error = load_json_file(filename)
    
    if error:
        return "", None, filename, f"Error: {error}"
    
    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    return json_text, json_text, filename, f"Loaded: {filename}"


@callback(
    Output('json-editor', 'value', allow_duplicate=True),
    Input('format-btn', 'n_clicks'),
    State('json-editor', 'value'),
    prevent_initial_call=True
)
def format_json(n_clicks, current_text):
    """Pretty-print the JSON in editor."""
    if not current_text:
        return no_update
    
    try:
        data = json.loads(current_text)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return no_update


@callback(
    Output('result-msg', 'children'),
    Output('result-msg', 'style'),
    Output('refresh-trigger', 'data'),
    Output('file-dropdown', 'value'),
    Input('save-btn', 'n_clicks'),
    State('json-editor', 'value'),
    State('original-json-store', 'data'),
    State('current-filename-store', 'data'),
    prevent_initial_call=True
)
def save_as_new_version(n_clicks, current_json, original_json, old_filename):
    """Validate, save as new version, and log changes."""
    
    base_style = {
        'marginTop': '20px',
        'padding': '15px',
        'textAlign': 'center',
        'borderRadius': '4px',
        'border': '1px solid #000'
    }
    
    # Validation: File selected?
    if not old_filename:
        return (
            "No file selected.",
            {**base_style, 'backgroundColor': '#fff'},
            no_update,
            no_update
        )
    
    # Validation: Content exists?
    if not current_json or not current_json.strip():
        return (
            "Editor is empty.",
            {**base_style, 'backgroundColor': '#fff'},
            no_update,
            no_update
        )
    
    # Validation: Valid JSON?
    try:
        new_data = json.loads(current_json)
    except json.JSONDecodeError as e:
        return (
            f"Invalid JSON: {e.msg} (line {e.lineno})",
            {**base_style, 'backgroundColor': '#fff'},
            no_update,
            no_update
        )
    
    # Check for changes
    changes = find_changes(original_json or "{}", current_json)
    
    if not changes:
        return (
            "No changes detected.",
            {**base_style, 'backgroundColor': '#fff'},
            no_update,
            no_update
        )
    
    # Generate new versioned filename
    user = get_current_user()
    new_filename = generate_versioned_filename(old_filename, user)
    
    # Save to NEW file
    success, message = save_json_file(new_filename, new_data)
    
    if not success:
        return (
            message,
            {**base_style, 'backgroundColor': '#fff'},
            no_update,
            no_update
        )
    
    # Log to audit with old_file and new_file
    log_audit(
        changes=changes,
        user=user,
        old_file=old_filename,
        new_file=new_filename
    )
    
    # Success - refresh list and select new file
    return (
        f"Saved {len(changes)} change(s): {old_filename} → {new_filename}",
        {**base_style, 'backgroundColor': '#f0f0f0'},
        datetime.now().timestamp(),
        new_filename  # Select the new file in dropdown
    )
