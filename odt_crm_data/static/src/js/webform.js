odoo.define('odt_crm_data.webform', [
    '@web/core/network/rpc_service'  // Dependencies must be listed as an array
], function () {
        'use strict';

            $(document).ready(function () {
            function containsArabicNumbers(value) {
            return /[٠-٩]/.test(value);
        }
        function hasArabicNumbers() {
            let found = false;
            $('input').each(function() {
                if (containsArabicNumbers($(this).val())) {
                    found = true;
                    return false;
                }
            });
            return found;
        }

                /******* ACTION: Changing the nationality to be 'other' *******/
                $('#nationality').on('change', function () {
                    console.log("Changing the nationality to others.")
                    // Elements and its value
                    var nationalityDropdown = document.getElementById("nationality");
                    var otherNationalityContainer = document.getElementById("other_nationality_container");
                    var selectedValue = nationalityDropdown.value;
                    // Check if the selected value corresponds to "Other"
                    if (selectedValue === "9999") {  // 9999 is the ID we assigned in Python to the 'Other' option
                        otherNationalityContainer.style.display = "block";
                        document.getElementById("other_nationality").setAttribute("required", "1");
                    } else {
                        otherNationalityContainer.style.display = "none";
                        document.getElementById("other_nationality").removeAttribute("required");
                    }
                });

///
                /******* ACTION: Clicking Button 2 *******/
                $('#number2_button').on('click', function () {
                console.log("heree using on click  function number2_button")
                console.log( $('#number1')[0])
                // getting data from form
                const date = $('input[name="date"]').val();
                const mobile = $('input[name="mobile"]').val();
                const name = $('input[name="name"]').val();
                const age = $('input[name="age"]').val()
                const gender = $('#gender').val()
                const profession = $('#profession').val()
                const job_title = $('input[name="job_title"]').val()
                const education_level = $('#education_level').val()
                const contact_name = $('input[name="contact_name"]').val()
                const contact_mobile = $('input[name="contact_mobile"]').val()
                const relation = $('input[name="relation"]').val()
                const errorMessage = document.getElementById('formErrorMessage');
                errorMessage.style.display = 'none'; // Hide error message by default
                // Handling If Nationality is 'other'
                const err = $('#formErrorMessage');
                err.hide();
                if (hasArabicNumbers()) {
                    err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                    return;
                }
                const nationality = $('#nationality').val()
                const other_nationality = $('#other_nationality').val()
                var other_nationality_error = false
                if (nationality == '9999' && !other_nationality){
                    other_nationality_error = true
                }
                // validate that all the important data is filled
                if (!name || !mobile || !date || !age || !nationality || !gender || !profession  || !education_level || !contact_name || !relation || !contact_mobile || other_nationality_error) {
                    errorMessage.innerText = '   من فضلك تاكد من البيانات الأولية  ';
                    errorMessage.style.display = 'flex';
                    return;
                }
                else{
                    $('#number1')[0].style.display = 'none'
                    $('#number2')[0].style.display = 'flex'
                    $('#number3')[0].style.display = 'none'
                    $('#number4')[0].style.display = 'none'
                    $('#number5')[0].style.display = 'none'
                    $('#number2_button')[0].style.display = 'none'
                    $('#number3_button')[0].style.display = 'flex'
                    $('#number4_button')[0].style.display = 'none'
                    $('#number5_button')[0].style.display = 'none'
                    $('#number6_button')[0].style.display = 'none'
                    console.log("00000000000000000000000")
                    console.log($('#number1_button_return'))
                    $('#number1_button_return')[0].style.display = 'flex'
                    $('#number2_button_return')[0].style.display = 'none'
                    $('#number3_button_return')[0].style.display = 'none'
                    $('#number4_button_return')[0].style.display = 'none'
                    }
                    }
                );


                /******* ACTION: Clicking Button 3 *******/
                $('#number3_button').on('click', function () {
                    const marital = $('#marital').val()
                    const family_member = $('input[name="family_member"]').val()
                    const working_member = $('input[name="working_member"]').val()
                    const primary_provider = $('#primary_provider').val()
                    const errorMessage = document.getElementById('formErrorMessage');
                    errorMessage.style.display = 'none'; // Hide error message by default
                    const err = $('#formErrorMessage');
                    err.hide();
                    if (hasArabicNumbers()) {
                        err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                        return;
                    }
                    if (!marital || !family_member || !working_member || !primary_provider ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع الاجتماعي  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    else{
                        //divs
                        $('#number1')[0].style.display = 'none'
                        $('#number2')[0].style.display = 'none'
                        $('#number3')[0].style.display = 'flex'
                        $('#number4')[0].style.display = 'none'
                        $('#number5')[0].style.display = 'none'
                        // buttons
                        $('#number2_button')[0].style.display = 'none'
                        $('#number3_button')[0].style.display = 'none'
                        $('#number4_button')[0].style.display = 'flex'
                        $('#number5_button')[0].style.display = 'none'
                        $('#number6_button')[0].style.display = 'none'
                        // return buttons
                        $('#number1_button_return')[0].style.display = 'none'
                        $('#number2_button_return')[0].style.display = 'flex'
                        $('#number3_button_return')[0].style.display = 'none'
                        $('#number4_button_return')[0].style.display = 'none'
                    }
                });


                /******* ACTION: Clicking Button 4 *******/
                $('#number4_button').on('click', function () {
                    //validation
                    const residence_area = $('#residence_area').val()
                    const residence_city = $('input[name="residence_city"]').val()
                    const residence_district = $('input[name="residence_district"]').val()
                    const residence_type = $('#residence_type').val()
                    const residence_ownership = $('#residence_ownership').val()
                    const annual_rent = $('input[name="annual_rent"]').val();
                    const annual_rent_doc = $('input[name="annual_rent_doc"]').val();
                    const errorMessage = document.getElementById('formErrorMessage');
                    errorMessage.style.display = 'none'; // Hide error message by default
                    const err = $('#formErrorMessage');
                    err.hide();
                    if (hasArabicNumbers()) {
                        err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                        return;
                    }
                    if (annual_rent && !annual_rent_doc) {
                        errorMessage.innerText = '   من فضلك، قم برفع عقد الإيجار السنوى ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    if (!residence_area || !residence_city || !residence_district || !residence_type || !residence_ownership ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع السكني  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    else{
                       // divs
                        $('#number1')[0].style.display = 'none'
                        $('#number2')[0].style.display = 'none'
                        $('#number3')[0].style.display = 'none'
                        $('#number4')[0].style.display = 'flex'
                        $('#number5')[0].style.display = 'none'
                        // buttons
                        $('#number2_button')[0].style.display = 'none'
                        $('#number3_button')[0].style.display = 'none'
                        $('#number4_button')[0].style.display = 'none'
                        $('#number5_button')[0].style.display = 'flex'
                        $('#number6_button')[0].style.display = 'none'
                        // return buttons
                        $('#number1_button_return')[0].style.display = 'none'
                        $('#number2_button_return')[0].style.display = 'none'
                        $('#number3_button_return')[0].style.display = 'flex'
                        $('#number4_button_return')[0].style.display = 'none'
                    }
                });


                /******* ACTION: Clicking Button 5 *******/
                $('#number5_button').on('click', function () {
                    const income_source = $('#income_source').val()
                    const monthly_income = $('input[name="monthly_income"]').val()
                    const income_doc = $('input[name="income_doc"]').val();
                    const errorMessage = document.getElementById('formErrorMessage');
                    errorMessage.style.display = 'none'; // Hide error message by default
                    const err = $('#formErrorMessage');
                    err.hide();
                    if (hasArabicNumbers()) {
                        err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                        return;
                    }
                    if (!income_source || !monthly_income || !income_doc ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع الاقتصادي  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    else{
                        // divs
                        $('#number1')[0].style.display = 'none'
                        $('#number2')[0].style.display = 'none'
                        $('#number3')[0].style.display = 'none'
                        $('#number4')[0].style.display = 'none'
                        $('#number5')[0].style.display = 'flex'
                        // buttons
                        $('#number2_button')[0].style.display = 'none'
                        $('#number3_button')[0].style.display = 'none'
                        $('#number4_button')[0].style.display = 'none'
                        $('#number5_button')[0].style.display = 'none'
                        $('#number6_button')[0].style.display = 'flex'
                        // return buttons
                        $('#number1_button_return')[0].style.display = 'none'
                        $('#number2_button_return')[0].style.display = 'none'
                        $('#number3_button_return')[0].style.display = 'none'
                        $('#number4_button_return')[0].style.display = 'flex'
                    }
                });


                /******* ACTION: Clicking Button Return 1 *******/
                $('#number1_button_return').on('click', function () {
            const err = $('#formErrorMessage');
            err.hide();
            if (hasArabicNumbers()) {
                err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                return;
            }
            // Proceed only if no Arabic numbers
            $('#number1')[0].style.display = 'flex';
            $('#number2')[0].style.display = 'none';
            $('#number3')[0].style.display = 'none';
            $('#number4')[0].style.display = 'none';
            $('#number5')[0].style.display = 'none';
            $('#number2_button')[0].style.display = 'flex';
            $('#number3_button')[0].style.display = 'none';
            $('#number4_button')[0].style.display = 'none';
            $('#number5_button')[0].style.display = 'none';
            $('#number6_button')[0].style.display = 'none';
            $('#number1_button_return')[0].style.display = 'none';
            $('#number2_button_return')[0].style.display = 'none';
            $('#number3_button_return')[0].style.display = 'none';
            $('#number4_button_return')[0].style.display = 'none';
        });

        /******* ACTION: Clicking Button Return 2 *******/
        $('#number2_button_return').on('click', function () {
            const err = $('#formErrorMessage');
            err.hide();
            if (hasArabicNumbers()) {
                err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                return;
            }
            // Proceed only if no Arabic numbers
            $('#number1')[0].style.display = 'none';
            $('#number2')[0].style.display = 'flex';
            $('#number3')[0].style.display = 'none';
            $('#number4')[0].style.display = 'none';
            $('#number5')[0].style.display = 'none';
            $('#number2_button')[0].style.display = 'none';
            $('#number3_button')[0].style.display = 'flex';
            $('#number4_button')[0].style.display = 'none';
            $('#number5_button')[0].style.display = 'none';
            $('#number6_button')[0].style.display = 'none';
            $('#number1_button_return')[0].style.display = 'flex';
            $('#number2_button_return')[0].style.display = 'none';
            $('#number3_button_return')[0].style.display = 'none';
            $('#number4_button_return')[0].style.display = 'none';
        });

        /******* ACTION: Clicking Button Return 3 *******/
        $('#number3_button_return').on('click', function () {
            const err = $('#formErrorMessage');
            err.hide();
            if (hasArabicNumbers()) {
                err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                return;
            }
            // Proceed only if no Arabic numbers
            $('#number1')[0].style.display = 'none';
            $('#number2')[0].style.display = 'none';
            $('#number3')[0].style.display = 'flex';
            $('#number4')[0].style.display = 'none';
            $('#number5')[0].style.display = 'none';
            $('#number2_button')[0].style.display = 'none';
            $('#number3_button')[0].style.display = 'none';
            $('#number4_button')[0].style.display = 'flex';
            $('#number5_button')[0].style.display = 'none';
            $('#number6_button')[0].style.display = 'none';
            $('#number1_button_return')[0].style.display = 'none';
            $('#number2_button_return')[0].style.display = 'flex';
            $('#number3_button_return')[0].style.display = 'none';
            $('#number4_button_return')[0].style.display = 'none';
        });

        /******* ACTION: Clicking Button Return 4 *******/
        $('#number4_button_return').on('click', function () {
            const err = $('#formErrorMessage');
            err.hide();
            if (hasArabicNumbers()) {
                err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                return;
            }
            // Proceed only if no Arabic numbers
            $('#number1')[0].style.display = 'none';
            $('#number2')[0].style.display = 'none';
            $('#number3')[0].style.display = 'none';
            $('#number4')[0].style.display = 'flex';
            $('#number5')[0].style.display = 'none';
            $('#number2_button')[0].style.display = 'none';
            $('#number3_button')[0].style.display = 'none';
            $('#number4_button')[0].style.display = 'none';
            $('#number5_button')[0].style.display = 'flex';
            $('#number6_button')[0].style.display = 'none';
            $('#number1_button_return')[0].style.display = 'none';
            $('#number2_button_return')[0].style.display = 'none';
            $('#number3_button_return')[0].style.display = 'flex';
            $('#number4_button_return')[0].style.display = 'none';
        });


                /******* ACTION: Clicking Button Return 1 *******/
                $('#number5_button_return').on('click', function () {
                    // divs
                    $('#number1')[0].style.display = 'none'
                    $('#number2')[0].style.display = 'none'
                    $('#number3')[0].style.display = 'none'
                    $('#number4')[0].style.display = 'none'
                    $('#number5')[0].style.display = 'flex'
                    // buttons
                    $('#number2_button')[0].style.display = 'none'
                    $('#number3_button')[0].style.display = 'none'
                    $('#number4_button')[0].style.display = 'none'
                    $('#number5_button')[0].style.display = 'none'
                    $('#number6_button')[0].style.display = 'flex'
                    // return buttons
                    $('#number1_button_return')[0].style.display = 'none'
                    $('#number2_button_return')[0].style.display = 'none'
                    $('#number3_button_return')[0].style.display = 'none'
                    $('#number4_button_return')[0].style.display = 'none'
                    $('#number5_button_return')[0].style.display = 'flex'
                    const errorMessage = document.getElementById('formErrorMessage');
                    errorMessage.style.display = 'none'; // Hide error message by default
                    const err = $('#formErrorMessage');
                    err.hide();
                    if (hasArabicNumbers()) {
                        err.text('يجب إدخال الأرقام باللغة الإنجليزية').show();
                        return;
                    }
                });


                /******* ACTION: Clicking Button Return 1 *******/
                $('#submit_button').on('click', function (e) {
                    console.log('kkkkkkkkkkkkkkkkkk')
                    // Validate required fields
                    // div 1
                    const date = $('input[name="date"]').val();
                    const mobile = $('input[name="mobile"]').val();
                    const name = $('input[name="name"]').val();
                    const age = $('input[name="age"]').val()
                    const nationality = $('#nationality').val()
                    const gender = $('#gender').val()
                    const profession = $('#profession').val()
                    const job_title = $('input[name="job_title"]').val()
                    const education_level = $('#education_level').val()
                    const contact_name = $('input[name="contact_name"]').val()
                    const contact_mobile = $('input[name="contact_mobile"]').val()
                    const relation = $('input[name="relation"]').val()
                    // div 2
                    const marital = $('#marital').val()
                    const family_member = $('input[name="family_member"]').val()
                    const working_member = $('input[name="working_member"]').val()
                    const primary_provider = $('#primary_provider').val()
                    // div 3
                    const residence_area = $('#residence_area').val()
                    const residence_city = $('input[name="residence_city"]').val()
                    const residence_district = $('input[name="residence_district"]').val()
                    const residence_type = $('#residence_type').val()
                    const residence_ownership = $('#residence_ownership').val()
                    // div 4
                    const income_source = $('#income_source').val()
                    const monthly_income = $('input[name="monthly_income"]').val()
                    // div 5
                    const health_status = $('#health_status').val()
                    const insurance_exists = $('#insurance_exists').val();
                    const insurance_doc = $('input[name="insurance_doc"]').val();
                    const required_action = $('#required_action').val()
                    const recent_medical_report = $('input[name="recent_medical_report"]').val()
                    const national_id_image = $('input[name="national_id_image"]').val()
                    const errorMessage = document.getElementById('formErrorMessage');
                    errorMessage.style.display = 'none'; // Hide error message by default
//                    if (hasArabicNumbers()) {
//                        errorMessage.innerText = 'يجب إدخال الأرقام باللغة الإنجليزية';
//                        errorMessage.style.display = 'flex';
//                        return;
//                    }
                    // Checking that al important data is filled
                    if (!name || !mobile || !date || !age || !nationality || !gender || !profession  || !education_level || !contact_name || !relation || !contact_mobile) {
                        console.log('jjjjjjjjjjjjjjjj')
                        errorMessage.innerText = '   من فضلك تاكد من البيانات الأولية  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    if (!marital || !family_member || !working_member || !primary_provider ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع الاجتماعي  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    if (!residence_area || !residence_city || !residence_district || !residence_type || !residence_ownership ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع السكني  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                    if (!income_source || !monthly_income  ) {
                        errorMessage.innerText = '   من فضلك تاكد من الوضع الاقتصادي  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
//                    if (insurance_exists === "yes" && !insurance_doc) {
//                        errorMessage.innerText = '   من فضلك، قم برفع التامين الطبي ';
//                        errorMessage.style.display = 'flex';
//                        e.preventDefault();
//                        return;
//                    }


                     if (!health_status || !monthly_income  || !required_action || !recent_medical_report || !national_id_image) {
                        errorMessage.innerText = '   من فضلك تاكد من الحالة الصحية  ';
                        errorMessage.style.display = 'flex';
                        return;
                    }
                })
            }
        );
     }
);
