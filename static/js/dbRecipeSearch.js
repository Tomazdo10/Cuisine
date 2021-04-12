/*jshint esversion: 6 */
$("document").ready(function () {
    let srcForm = $("form[name=search-form]");
    let recipesRow = $("#recipe-display-row");
    let loader = $("#loader");

    srcForm.submit(function (event) {
        let data = srcForm.serialize();


        $ajax({
            url: "recipes/search/",
            type: "POST",
            data: data,
            dataType: "json",
            beforeSend: function () {
                recipesRow.empty();
                let loaderCopy = loader.clone().contents();

                recipesRow.append(loaderCopy);
            },
            success: function (resp) {
                recipesRow.empty();
                for (i = 0; i < resp.length; i++) {
                    let cardTemplateCopy = $("#card-template").clone().contents();

                    cardTemplateCopy.find("img").attr("src", resp[i].img_url);
                    cardTemplateCopy.find("#card-heading").text(resp[i].recipe_name);
                    cardTemplateCopy.find("#collapse-btn").attr("href", "#collapse" + i + 1);
                    cardTemplateCopy.find(".collapse").attr("id", "collapse" + i + 1);
                    cardTemplateCopy.find("p").text(resp[i].step_description[1]);
                    cardTemplateCopy.find("#read-more-btn").attr("#href", "/view/recipe/" + resp[i]._id.$oid);

                    recipesRow.append(cardTemplateCopy);
                }
            },
            error: function (resp) {
                recipesRow.empty();
                let noRecipesFound = '<div class="col-12 text-center mb-5"><h2 class="text-danger">No Recipes Found</h2><p>Try Search for something else.</p></div>';
                $("#recipe-display-row").prepend(noRecipesFound);

                for (i = 0; i < resp.responseJSON.length; i++) {
                    let cardTemplateCopy = $("#card-template").clone().contents();

                    cardTemplateCopy.find("img").attr("src", resp.responseJSON[i].img_url);
                    cardTemplateCopy.find("#card-heading").text(resp.responseJSON[i].recipe_name);
                    cardTemplateCopy.find("#collapse-btn").attr("href", "#collapse" + i + 1);
                    cardTemplateCopy.find(".collapse").attr("id", "collapse" + i + 1);
                    cardTemplateCopy.find("p").text(resp.responseJSON[i].step_description[1]);
                    cardTemplateCopy.find("#read-more-btn").attr("href", "/wiev_recipe/" + resp.responseJSON[i]._id.$oid);

                    recipesRow.append(cardTemplateCopy);
                }
            }
        });

        event.preventDefault();
    });
});