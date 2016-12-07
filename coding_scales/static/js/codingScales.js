resultsTemplate = "<div class='container'><h1 class='text-center'>Good Work!</h1><p class='lead text-center'>Here are your results</p><div class='panel-group'><div class='col-md-12'><div class='panel panel-default'><div class='panel-heading'>Results</div><div class='panel-body'><table class='table table-bordered table-hover table-condensed table-striped'><thead class='thead-inverse'><tr><th><strong>hello-world.py</strong></th><th>time</th><th>keystrokes</th></tr></thead><tr class='success'><td><strong>You</strong></td><td>{{your_time}}</td><td>{{your_keypresses}}</td></tr><tr><td><strong>Percentile</strong></td><td>{{percentile_of_time}}</td><td>{{percentile_of_keypresses}}</td></tr><tr><td><strong>Min</strong></td><td>{{min_time}}</td><td>{{min_keypresses}}</td></tr><tr><td><strong>Max</strong></td><td>{{max_time}}</td><td>{{max_keypresses}}</td></tr><tr><td><strong>Average</strong></td><td>{{avg_time}}</td><td>{{avg_keypresses}}</td></tr><tr><td><strong>Median</strong></td><td>{{median_time}}</td><td>{{median_keypresses}}</td></tr></table></div></div></div></div></div>"
exerciseTemplate = "<script src='static/mode/{{ language }}/{{ language }}.js'></script><div id='{{ id }}' class='panel panel-default'><div class='panel-heading text-center'><h3>{{ name }}</h3></div><div class='panel-body row'><div class='col-md-6'><h4 class='text-center'>type this</h4><hr /><textarea id='exercise-text'>{{ text }}</textarea></div><div class='col-md-6'><h4 class='text-center'>here</h4><hr /><textarea id='exercise-editor'></textarea></div></div></div>"
exerciseRowTemplate = "<tr class='exercise' id='{{ id }}'><td>{{ name }}</td><td>{{ language }}</td><td>{{ author_id }}</td><td>{{ date_added }}</td></tr>"
exerciseCollectionTemplate = "<div class='panel panel-default'><button class='btn-inverse pull-right' id='last-page'><span class='glyphicon glyphicon-fast-forward' aria-hidden='true'></span></button><button class='btn-inverse pull-right' id='next-page'><span class='glyphicon glyphicon-forward' aria-hidden='true'></span></button><button class='btn-inverse pull-right' id='previous-page'><span class='glyphicon glyphicon-backward' aria-hidden='true'></span></button><button class='btn-inverse pull-right' id='first-page'><span class='glyphicon glyphicon-fast-backward' aria-hidden='true'></span></button><div class='panel-heading'>Exercises</div><table class='table table-striped table-bordered table-hover table-sm'><tr><th>name</th><th>language</th><th>author-id</th><th>date-added</th>{{{ rows }}}</tr></table><button class='btn-inverse pull-right' id='add-exercise'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button></div>"
Mustache.parse(resultsTemplate)
Mustache.parse(exerciseTemplate)
Mustache.parse(exerciseRowTemplate)
Mustache.parse(exerciseCollectionTemplate)



var Timer = function( ){
    var self = this;
    self.time = 0;
    window.setInterval(function(){
        self.time = self.time + 1;
    }, 1000)
}

var Exercise = function( obj ){
    var self = this;
    self.author_id  = obj.author_id;
    self.date_added = obj.date_added;
    self.id         = obj.id;
    self.language   = obj.language;
    self.name       = obj.name;
    self.text       = obj.text;
    self.keypresses = 0;

    self.renderRow = function(){
        return Mustache.render( exerciseRowTemplate, self );
    };

    self.render = function( elem ){
        self.timer = new Timer();
        elem.html( Mustache.render( exerciseTemplate, self ) );
        var editor = CodeMirror.fromTextArea(
            document.getElementById("exercise-editor"),
            {
                lineNumbers: true,
                mode: self.language,
                autofocus: true
            }
        );
        var challenge = CodeMirror.fromTextArea(
            document.getElementById("exercise-text"),
            {
                readOnly: "nocursor",
                lineNumbers: true,
                mode: self.language
            }
        );
        challenge.on("beforeSelectionChange", function( cm, e ){
            e.preventDefault();
            challenge.signal("update");
            editor.signal("focus");
        });
        editor.on("paste", function( cm, e ){
            e.preventDefault();
        });
        editor.on("change", function( cm, chg ){
            if ( cm.getValue() === challenge.getValue() ){
                data = {
                    "exercise_id": self.id,
                    "time": self.timer.time,
                    "keypresses": self.keypresses
                }
                $.ajax({
                    url: "/results",
                    type: "POST",
                    data: JSON.stringify(data),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function( data ){
                        $( "#display" ).html(Mustache.render(resultsTemplate, data));
                    }
                });
            }
        });
        editor.on("keypress", function(){
            self.keypresses = self.keypresses + 1
        });
    };
};

var ExerciseCollection = function(  elem, page=1 ){
    var self = this;
    self.page = page;
    self.uri = "/exercises?page="+page;
    self.elem = elem

    self.render = function( elem ){
        $.getJSON(self.uri, function( data ){
            var rowsHTML = ""
            $.each(data, function( index, obj ){
                self.page = obj["page"];
                self.pages = obj["pages"];
                exercise = new Exercise( obj );
                rowsHTML = rowsHTML + exercise.renderRow();
            });
            elem.html(Mustache.render( exerciseCollectionTemplate, {rows: rowsHTML} ));
        }).fail(function(){
            if (self.page > 1 ){
                self.page = self.page - 1;
            } else {
                self.page = 1;
            }
        });
    };
};

$( document ).ready(function(){
    collection = new ExerciseCollection( $( "#display" ) );
    collection.render( $( "#display" ) );

    $( "body" ).on("click", ".exercise", function( event ){
        var row = $( event.target ).parent();
        var id = row.attr("id");
        $.getJSON( "/exercises/" + id, function( data ){
            exercise = new Exercise( data );
            exercise.render( $( "#display" ) );
        } );
    });

    $( "body" ).on("click", "#add-exercise", function( event ){
        $( "#display" ).html("<form action='exercises' method='POST'><div class='form-group'><label for='name'>name</label><input type='textbox' class='form-control' name='name' id='name' /><br /><label for='language'>language</label><input type='textbox' class='form-control' name='language' id='language' /><br /><label for='text'>body</label><textarea id='exercise-body'></textarea><br /><button class='btn btn-lg btn-inverse btn-block' id='submit-exercise' type='submit'>Submit</button></div></form>");
        var editor = CodeMirror.fromTextArea(
            document.getElementById("exercise-body"),
            {lineNumbers: true}
        );
    });

    $ ( "body" ).on("click", "#submit-exercise", function( event ){
        event.preventDefault();
        data = {
            name: $( 'input[name=name]' ).val(),
            language: $( 'input[name=language]' ).val(),
            text: $('.CodeMirror')[0].CodeMirror.getValue()
        };
        $.ajax({
            url: '/exercises',
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function( data ){
                var collection = new ExerciseCollection( $( "#display" ) );
                collection.render( $( "#display" ) );
            }
        });
    });

    $( "#show-exercises" ).on("click", function( event ){
        collection.render( $( "#display" ) );
    });
    $( "body" ).on("click", "#next-page", function( event ){
        var page = collection.page + 1;
        if (page > collection.pages){
            return
        }
        collection = new ExerciseCollection( $( "#display" ), page );
        collection.render( $( "#display" ) )
    });
    $( "body" ).on("click", "#previous-page", function( event ){
        var page = collection.page - 1;
        if ( page < 1 ){
            return
        }
        collection = new ExerciseCollection( $( "#display" ), page );
        collection.render( $( "#display" ) )
    });
    $( "body" ).on("click", "#first-page", function( event ){
        if ( collection.page === 1 ){
            return
        }
        var page = 1;
        collection = new ExerciseCollection( $( "#display" ), page );
        collection.render( $( "#display" ) )
    });
    $( "body" ).on("click", "#last-page", function( event ){
        if ( collection.page === collection.pages ){
            return
        }
        var page = collection.pages;
        collection = new ExerciseCollection( $( "#display" ), page );
        collection.render( $( "#display" ) )
    });
});
