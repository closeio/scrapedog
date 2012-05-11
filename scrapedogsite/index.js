$(function(){

	$("#submit_url").click(function(){
		
		var url = $("[name='url']").val();
		$(".midblock").html('<iframe src='+url+'>');
		
		$.ajax({
			type: "GET",
			dataType: 'jsonp',
			contentType: "application/json",
			jsonpCallback: 'jsonCallback',
			data: { url : url },
			url: "http://scrapedog.herokuapp.com/test?callback=?"
		});
	});
	

})

function jsonCallback(test)
{
	console.log(test);
	$(".leftblock").text('');
	$(".leftblock").append('<div class="result-url">URL: '+test.url+'</div>');
	$(".leftblock").append('<div class="result-title">Title: '+test.title+'</div>');
	for (var i = 0; i < test.meta_tags.length; i++)
	{
		$(".leftblock").append('<div class="result-meta-tags">Meta Tags: '+JSON.stringify(test.meta_tags[i])+'</div>');
	}
	for (var x = 0; x < test.phone_tags.length; x++)
	{
		$(".leftblock").append('<div class="result-phone-tags">'+test.phone_tags[x]+'</div>');
	}	
	if (test.contacts != undefined)
	{
		for (var z=0; z < test.contacts.length; z++)
		{
			$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.name+'</div>')
			for (var a=0; a< test.contacts.phones.length ; a++)
			{
				$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.phones[a]+'</div>')
			}
			for (var a=0; a< test.contacts.emails.length ; a++)
			{
				$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.emails[a]+'</div>')
			}
			for (var a=0; a< test.contacts.urls.length ; a++)
			{
				$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.urls[a]+'</div>')
			}
			for (var a=0; a< test.contacts.addresses.length ; a++)
			{
				$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.addresses[a]+'</div>')
			}
			$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.title+'</div>')
			$(".leftblock").append('<div class="result-contact-'+z+'>'+test.contacts.company+'</div>')
		}
	}
}
	
