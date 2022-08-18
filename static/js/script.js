window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteButton =document.querySelectorAll('.delButton');

for (let i=0; i<deleteButton.length; i++){
  const Dbtn= deleteButton[i];
  Dbtn.onclick = function(e){
    const VenueId =e.target.dataset['id'];
    fetch('/venues/' + VenueId, {
      method:'DELETE'
    });
  }
}

const ArtUp= document.querySelectorAll('#ArtistUpdate');
for (let i=0; i<ArtUp.length; i++) {
  ArtUp.onclick = function(e){
    const NewArtUpdate = e.target.submitted
    const ArtistId =e.target.dataset['id'];
    fetch('/artists/'+ ArtistId + '/edit', {
      method:'POST',
      body: JSON.stringify({
        'artist': NewArtUpdate

      }),
      headers: {
        'Content-Type':'application/json'
      }

    })
  }
}



const VenUp= document.querySelectorAll('#VenueUpdate');
for (let i=0; i<ArtUp.length; i++) {
  ArtUp.onclick = function(e){
    const NewVenUpdate = e.target.submitted
    const VenueId =e.target.dataset['id'];
    fetch('/venues/'+ VenueId + '/edit', {
      method:'POST',
      body: JSON.stringify({
        'venue': NewVenUpdate

      }),
      headers: {
        'Content-Type':'application/json'
      }

    })
  }
}