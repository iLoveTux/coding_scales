exerciseTemplate = "<script src='static/mode/{{ language }}/{{ language }}.js'></script><div id='{{ id }}' class='panel panel-default'><div class='panel-heading text-center'><h3>{{ name }}</h3></div><div class='panel-body row'><div class='col-md-6'><h4 class='text-center'>type this</h4><hr /><textarea id='exercise-text'>{{ text }}</textarea></div><div class='col-md-6'><h4 class='text-center'>here</h4><hr /><textarea id='exercise-editor'></textarea></div></div></div>"
exerciseRowTemplate = "<tr class='exercise' id='{{ id }}'><td>{{ name }}</td><td>{{ language }}</td><td>{{ author_id }}</td><td>{{ date_added }}</td></tr>"
exerciseCollectionTemplate = "<div class='panel panel-default'><div class='panel-heading'>Exercises</div><table class='table table-striped table-bordered table-hover table-sm'><tr><th>name</th><th>language</th><th>author-id</th><th>date-added</th>{{{ rows }}}</tr></table></div>"
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
                        alert(JSON.stringify(data));
                    }
                });
            }
        });
        editor.on("keypress", function(){
            self.keypresses = self.keypresses + 1
        });
    };
};

var ExerciseCollection = function(  elem ){
    var self = this;
    self.uri = "/exercises";
    self.elem = elem

    self.render = function( elem ){
        $.getJSON(self.uri, function( data ){
            var rowsHTML = ""
            $.each(data, function( index, obj ){
                exercise = new Exercise( obj );
                rowsHTML = rowsHTML + exercise.renderRow();
            });
            elem.html(Mustache.render( exerciseCollectionTemplate, {rows: rowsHTML} ));
        });
    };
};

$( document ).ready(function(){
    var collection = new ExerciseCollection( $( "#display" ) );
    collection.render( $( "#display" ) );

    $( "body" ).on("click", ".exercise", function( event ){
        var row = $( event.target ).parent();
        var id = row.attr("id");
        $.getJSON( "/exercises/" + id, function( data ){
            exercise = new Exercise( data );
            exercise.render( $( "#display" ) );
        } );
    });

    $( "#show-exercises" ).on("click", function( event ){
        collection.render( $( "#display" ) );
    });
});
