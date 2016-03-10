var add_comment_url = '{{ url_for('users.add_comment', _external=True) }}';
var get_comment_url = '{{ url_for('users.get_comments', _external=True) }}';
var profile_url = '{{ url_for('static', filename='images/profile_pictures/', _external=True) }}';
var delete_comment_url = '{{ url_for('users.delete_comment', _external=True) }}';
var model_path = '{{ url_for('static', filename='models/building_models/', _external=True) }}';
var base_url = '{{ url_for('index', _external=True) }}';

var ADD_COMMENT_URL = '{{ url_for('users.add_comment', _external=True) }}';
var GET_COMMENT_URL = '{{ url_for('users.get_comments', _external=True) }}';
var PROFILE_URL = '{{ url_for('static', filename='images/profile_pictures/', _external=True) }}';
var DELETE_COMMENT_URL = '{{ url_for('users.delete_comment', _external=True) }}';
var MODEL_PATH = '{{ url_for('static', filename='models/building_models/', _external=True) }}';
var BASE_URL = '{{ url_for('index') }}';
var UPDATE_SCENARIO_URL = '{{ url_for('sketchup.update_scenario', scenario_id='') }}';
var UPDATE_BUILDING_MODEL_URL = '{{ url_for('sketchup.update_building_model', building_model_id='') }}';