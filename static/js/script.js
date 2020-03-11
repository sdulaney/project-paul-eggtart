  $(document).ready(function(){
    $('input.autocomplete').autocomplete({
      data: {
        "Tian Ye": null,
        "Jeff Bezos": null,
        "Tim Cook": null,
        "Paul Eggert": null,
        "Jack Ma": null,
        "Faker Hung": null,
        "Elon Musk": null,
        "Michael Pie": null,
        "Lebron James": null
      }
    });
    $(".dropdown-trigger").dropdown();
  });

