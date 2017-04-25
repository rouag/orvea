!function (document, window, $) {
    "use strict";

    /*---- Select2 ----*/

    $(".js-example-basic-single").select2();
    $(".js-example-basic-multiple").select2();


    $(".js-example-placeholder-single").select2({
        placeholder: "Select a state",
        allowClear: true
    });
    var data = [{id: 0, text: 'enhancement'}, {id: 1, text: 'bug'}, {id: 2, text: 'duplicate'}, {
        id: 3,
        text: 'invalid'
    }, {id: 4, text: 'wontfix'}];

    $(".js-example-data-array").select2({
        data: data
    });
    $(".js-programmatic-enable").on("click", function () {
        $(".js-example-disabled").prop("disabled", false);
        $(".js-example-disabled-multi").prop("disabled", false);
    });

    $(".js-programmatic-disable").on("click", function () {
        $(".js-example-disabled").prop("disabled", true);
        $(".js-example-disabled-multi").prop("disabled", true);
    });
    $(".js-example-basic-multiple-limit").select2({
        maximumSelectionLength: 2
    });
    $(".js-example-basic-hide-search").select2({
        minimumResultsForSearch: Infinity
    });
    $(".js-example-tags").select2({
        tags: true
    })
    function formatState(state) {
        if (!state.id) {
            return state.text;
        }
        var $state = $(
            '<span><img src="../../..//smart_internal_portal/static/src/assets/global/image/' + state.element.value.toLowerCase() + '.png" class="img-flag" /> ' + state.text + '</span>'
        );
        return $state;
    };

    $(".js-example-templating").select2({
        templateResult: formatState
    });

    /*---- Typeahead ----*/


    var substringMatcher = function (strs) {
        return function findMatches(q, cb) {
            var matches, substringRegex, substrRegex;

            matches = [];

            substrRegex = new RegExp(q, 'i');

            $.each(strs, function (i, str) {
                if (substrRegex.test(str)) {
                    matches.push(str);
                }
            });

            cb(matches);
        };
    };

    var states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
        'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
        'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
        'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
        'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
        'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
        'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
        'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
        'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ];

    $('#the-basics .typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'states',
            source: substringMatcher(states)
        });

    var state = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        local: states
    });

    $('#bloodhound .typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'states',
            source: state
        });

    var countries = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: '../../..//smart_internal_portal/static/src/assets/global/js/global/data/countries.json'
    });

    $('#prefetch .typeahead').typeahead(null, {
        name: 'countries',
        source: countries
    });

    var nflTeams = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        identify: function (obj) {
            return obj.team;
        },
        prefetch: '../../..//smart_internal_portal/static/src/assets/global/js/global/data/nfl.json'
    });

    function nflTeamsWithDefaults(q, sync) {
        if (q === '') {
            sync(nflTeams.get('Detroit Lions', 'Green Bay Packers', 'Chicago Bears'));
        }

        else {
            nflTeams.search(q, sync);
        }
    }

    $('#default-suggestions .typeahead').typeahead({
            minLength: 0,
            highlight: true
        },
        {
            name: 'nfl-teams',
            display: 'team',
            source: nflTeamsWithDefaults
        });

    var nbaTeams = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: '../../..//smart_internal_portal/static/src/assets/global/js/global/data/nba.json'
    });

    var nhlTeams = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: '../../..//smart_internal_portal/static/src/assets/global/js/global/data/nhl.json'
    });

    $('#multiple-datasets .typeahead').typeahead({
            highlight: true
        },
        {
            name: 'nba-teams',
            display: 'team',
            source: nbaTeams,
            templates: {
                header: '<h6 class="league-name">NBA Teams</h6>'
            }
        },
        {
            name: 'nhl-teams',
            display: 'team',
            source: nhlTeams,
            templates: {
                header: '<h6 class="league-name">NHL Teams</h6>'
            }
        });


    $('#scrollable-dropdown-menu .typeahead').typeahead(null, {
        name: 'countries',
        limit: 10,
        source: countries
    });

    /*---- TouchSpin ----*/
    $('[data-plugin="TouchSpin"]').each(function () {
        var $this = $(this);
        $this.TouchSpin({});
    });

    /*---- Datetimepicker ----*/
   $('#fiscal').flatpickr({
        weekNumbers: true,
       wrap: true,
        getWeek: function(givenDate){
            var checkDate = new Date(givenDate.getTime());
            checkDate.setDate(checkDate.getDate() + 4 - (checkDate.getDay() || 7));
            var time = checkDate.getTime();
            checkDate.setMonth(7);
            checkDate.setDate(28);

            var week = (Math.floor(Math.round((time - checkDate) / 86400000) / 7) + 2);
            if (week < 1) {
                week = 52 + week;
            }

            return 'FW' + ("0" + week).slice(-2);
        }
    });
    $('#enable-date').flatpickr({
        enable: [
            {
                from: "today",
                to: new Date().fp_incr(7) // 7 days from now
            }
        ],
        wrap: true
    });
    $('#disable-date').flatpickr({
        disable: [
            { from: "2016-08-16", to: "2016-08-19" },
            "2016-08-24",
            new Date().fp_incr(30) // 30 days from now
        ],
        wrap: true
    });

    /*---- Timepicker ----*/
    $('[data-plugin="timepicker"]').each(function () {
        var $this = $(this);
        $this.timepicker({});
    });

    $('#setTimeButton').on('click', function (){
        $('#setTimeExample').timepicker('setTime', new Date());
    });

    $('#selectButton').click(function(e) {
        $('#selectExample').timepicker('option', { useSelect: true });
        $(this).hide();
        $('.iconbutton').hide();
    });

    /*---- colorpicker ----*/
    $('[data-plugin="colorpicker"]').each(function () {
        var $this = $(this);
        $this.colorpicker({});
    });

    $('#cp4').colorpicker().on('changeColor', function(e) {
        $('body')[0].style.backgroundColor = e.color.toString( 'rgba');
    });

    $(".disable-button").click(function(e) {
        e.preventDefault();
        $("#cp10").colorpicker('disable');
    });

    $(".enable-button").click(function(e) {
        e.preventDefault();
        $("#cp10").colorpicker('enable');
    });
    $('#cp10').colorpicker();



}(document, window, jQuery);
