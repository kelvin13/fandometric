$(document).ready(function() {
    namespace = '/py';
    
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    var confirm_what;
    var $command = $('#command');
    autosize($command);
    $command.val( $command.val().replace(/(\r\n|\n|\r)/gm,'') );
    
    function clear_and_show_command() {
        $command.val('');
        $('#console_input').show();
    }
    
    socket.on('open', clear_and_show_command);
    
    socket.on('confirmation', function(J) {
        confirm_what = J.command;
        clear_and_show_command();
        $('#active_prompt').text(J.prompt);
    });
    
    function kill_current() {
        console.log('kill');
        socket.emit('kill');
    }

    $command.keypress(function(k){
        if (k.keyCode == 13) {
            var value = $(this).val();
            if (confirm_what === undefined) {
                socket.emit('fm command', value);
                
            } else {
                socket.emit('fm confirm', {key: confirm_what, value: value});
                confirm_what = undefined;
                $('#active_prompt').text('');
            }
            $('#console_input').hide();
        }     
    });
    
    $(window).bind('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && (String.fromCharCode(event.which).toLowerCase() == 'e')) {
            kill_current();
        }
    });
    
    window.onunload = kill_current;
    
    function createTable(tableData, thData) {
        var table = document.createElement('table');
        var tableBody = document.createElement('tbody');

        tableData.forEach(function(rowData) {
            var row = document.createElement('tr');

            rowData.forEach(function(cellData) {
                var cell = document.createElement('td');
                if (cellData.constructor === Array) {
                    if (cellData[0]) {
                        cell.innerHTML = cellData[0];
                    }
                    if (cellData[1]) {
                        cell.className = cellData[1];
                    }
                } else {
                    cell.innerHTML = cellData;
                }
                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });
        
        if (thData !== undefined) {
            var tableHeader = document.createElement('thead');
            var th_row = document.createElement('tr');
            thData.forEach(function(cellText) {
                var th_cell = document.createElement('td');
                th_cell.innerHTML = cellText;
                th_row.appendChild(th_cell);
            });
            tableHeader.appendChild(th_row)
            table.appendChild(tableHeader)
        }
        table.appendChild(tableBody);
        return table
    }
    
    function Bubble(type, msg) {
        var bubble = $('<div class="bubble"></div>')
        if (msg) {
            bubble.text(msg)
        }
        switch(type) {
            case 'command':
                var prompt_wrapper = $('<div><div class="prompt dead-prompt"></div></div>')
                prompt_wrapper.append(bubble)
                return {bubble : bubble,
                        open   : false,
                        element: prompt_wrapper,
                        stream : function(status) {
                                    this.bubble.text('meta: Streaming to Command bubble not allowed');
                                }
                };
            case 'output':
                return {bubble : bubble,
                        open   : true,
                        element: bubble,
                        stream : function(status) {
                                    this.bubble.text(status);
                                }
                };
            case 'blog fetch':
                var progress = $('<div class="progress-bar"></div>')
                var progress_trough = $('<div class="progress-trough"></div>')
                progress_trough.append(progress)
                
                var bubble_text = $(document.createElement('div'))
                var bubble_text_status = $(document.createElement('span'))
                bubble_text.append(bubble_text_status)
                
                var bubble_color = $(document.createElement('div'))
                bubble_color.append(progress_trough, bubble_text)
                bubble.append(bubble_color)
                bubble.addClass('long-process')
                
                return {bubble : bubble,
                        open   : true,
                        element: bubble,
                        
                        bubble_color: bubble_color,
                        
                        bubble_text: bubble_text,
                        
                        bubble_text_status: bubble_text_status,
                        progress: progress,
                        
                        stream : function(status) {
                                    if (status.msg !== undefined) {
                                        this.bubble_text_status.text(status.msg)
                                        
                                        this.bubble_color.attr('class', status.color)
                                        if (status.percent !== undefined) {
                                            this.progress.css('width', status.percent + '%')
                                        }
                                    } else if (status.search_name !== undefined) {
                                        this.celebrity = $('<span class="celeb celeb-off">' + status.search_name + '</span>')
                                        this.bubble_text.append(this.celebrity)
                                    } else if (status.search_found !== undefined) {
                                        this.celebrity.removeClass('celeb-off').addClass('celeb-on')
                                    }
                                }
                };
            case 'error':
                bubble.addClass('error');
                return {bubble : bubble,
                        open   : false,
                        element: bubble,
                        stream : function(status) {
                                    this.bubble.text('meta: Streaming to Error bubble not allowed');
                                }
                };
            case 'exception':
                bubble.addClass('error exception');
                return {bubble : bubble,
                        open   : false,
                        element: bubble,
                        stream : function(status) {
                                    this.bubble.text('meta: Streaming to Exception bubble not allowed');
                                }
                };
        }
    }
    
    bubbles = [];
    
    socket.on('make bubble', function(data) {
        var bubble = Bubble(data.type, data.msg);
        bubbles[data.i] = bubble;
        $('#console_output').append(bubble.element);
    });

    socket.on('stream', function(data) {
        var target = bubbles[data.i];
        if (target === undefined || ! target.open) {
            kill_current();
        } else {
            target.stream(data.status);
        }
    });

    socket.on('table', function(data) {
        var table = $(document.createElement('div'));
        table.addClass(data.css_class);
        
        var T = createTable(data.table, data.thead);
        T.className = data.css_table_class;
        
        if (data.head !== undefined) {
            var head = document.createElement('div');
            head.innerHTML = data.head;
            head.className = data.css_head_class;
            table.append(head);
        }
        table.append(T);
        $('#details').append(table);
    });

    socket.on('element', function(data) {
        var E = document.createElement(data.tag);
        if (data.css_class) {
            E.className = data.css_class;
        }
        
        E.innerHTML = data.html;
        $('#details').append(E);
    });

    socket.on('need', function(command) {
        socket.emit('fm command', command);
    });
    socket.emit('connect');
    
});
