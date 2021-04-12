/*jshint esversion: 6 */
let $ajax;
let $;

$("document").ready(function () {
    let ingCount = 1;
    let desCount = 1;

    $("#add-ingredient").click(function (e) {
        if ($("#del-ingredient").hasClass("display-none")) {
            $("#del-ingredient").removeClass("display-none");
        }

        let ingredientTemplateCopy = $("#ingredient-template").clone().contentes();
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

    $("#add-step").click(function () {
        if ($("#del-step").hasClass("display-none")) {
            $("#del-step").removeClass("display-none");
        }

        let stepTemplateCopy = $("#step-template").clone().contents();
        desCount++;

        stepTemplateCopy.addClass("remove" + desCount);
        stepTemplateCopy.find("p").text(desCount + ".");

        $("#step-action-container").before(stepTemplateCopy);
    });

    $("#del-step").click(function (e) {
        let divClass = ".remove" + desCount;
        $(divClass).remove();
        desCount--;
        if (desCount == 1) {
            $("#del-step").addClass("display-none");
        }
    });

    $("form[name=add-recipe]").submit(function (event) {
        let data = $("#add-recipe").serialize();

        $ajax({
            url: "/add_recipe/insert_recipe",
            type: "POST",
            data: data,
            dataType: "json",
            success: function (resp) {
                window.location.href = "/profile_page/";
            }
        });

        event.preventDefault();
    });
});