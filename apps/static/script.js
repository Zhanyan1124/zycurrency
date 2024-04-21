function currencySelectionOption(option) {
    if (!option.id) {
    return option.text;
    }

    var imageUrl = $(option.element).data("image");
    if (!imageUrl) {
        return option.text;
    }

    var fav = $(option.element).data("fav")
    if (fav){
        return $(
            '<span> <img src="' + fav +'" style="width:15px;height:15px;margin-right:10px" /><img src="' +
                imageUrl +
                '" class="img-flag" style="width:25px;height:15px;margin-right:5px"/> ' +
                option.text +
                '</span> ' 
            );
    }
    else{
        return $(
        '<span><img src="' +
            imageUrl +
            '" class="img-flag" style="width:25px;height:15px;margin-right:5px"/> ' +
            option.text +
            "</span>" 
        );
    }
};