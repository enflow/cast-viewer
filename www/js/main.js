var getHash = function(){
    var hash = window.location.hash.replace(/^#/,'').split('&'),
        parsed = {};
 
    for(var i =0,el;i<hash.length; i++ ){
         el=hash[i].split('=')
         parsed[el[0]] = el[1];
    }
    return parsed;
 };
