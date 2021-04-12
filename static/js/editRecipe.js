/*jshint esversion: 6 */
let $;
$("document").ready(function () {
    let ingIndexArrayString = $(".ingredient-index").text().split('.').slice(0, -1);
    let i;
    let ingIndexArrayFloat = [];


    for (i = 0; i < ingIndexArrayString.length; i++) {
        let number = parseFloat(ingIndexArrayString[i]);

        ingIndexArrayFloat.push(number);
    }

    let ingCount = Math.max(...ingIndexArrayFloat);

    if (ingCount > 1 && $("#del-ingredient").hasClass("display-none")) {
        $("#del-ingredient").removeClass("display-none");
    }

    $("#add-ingredient").click(function (e) {
        if ($("#del-ingredient").hasClass("display-none")) {
            $("#del-ingredient").removeClass("display-none");
        }
        let ingredientTemplateCopy = $("#ingredient-template").clone().contents();
        ingCount++;

        ingredientTemplateCopy.addClass("remove" + ingCount);
        ingredientTemplateCopy.find("p").text(ingCount + ".");

        $("#ingredient-action-container").before(ingredientTemplateCopy);
    });

    $("#del-ingredient").click(function (e) {
        let divClass = ".remove" + ingCount;
        $(divClass).remove();
        ingCount--;
        if (ingCount == 1) {
            $("#del-ingredient").addClass("display-none");
        }
    });

    let stepIndexArrayString = $(".step-index").text().split('.').slice(0, -1);
    let x;
    let stepIndexArrayFloat = [];

    for (x = 0; x < stepIndexArrayString.length; x++) {
        let number = parseFloat(stepIndexArrayString[x]);

        stepIndexArrayFloat.push(number);
    }

    let stepCount = Math.max(...stepIndexArrayFloat);

    if (stepCount > 1 && $("#del-step").hasClass("display-none")) {
        $("#del-step").removeClass("display-none");
    }

    $("#add-step").click(function () {
        if ($("#del-step").hasClass("display-none")) {
            $("#del-step").removeClass("display-none");
        }

        let stepTemplateCopy = $("#step-template").clone().contents();
        stepCount++;

        stepTemplateCopy.addClass("remove" + stepCount);
        stepTemplateCopy.find("p").text(stepCount + ".");

        $("#step-action-container").before(stepTemplateCopy);
    });

    $("#del-step").click(function (e) {
        let divClass = ".remove" + stepCount;
        $(divClass).remove();
        stepCount--;
        if (stepCount == 1) {
            $("#del-step").addClass("display-none");
        }
    });
});