// disable drag n drop
document.addEventListener('dragstart', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}, true);

document.addEventListener('drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}, true);

document.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}, true);

document.addEventListener('dragenter', function(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}, true);