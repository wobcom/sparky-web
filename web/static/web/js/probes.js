const toggleRouteModal = document.getElementById('toggleRouteModal')
toggleRouteModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget

  const route_id = button.getAttribute('data-bs-route-id')
  const route_enabled = button.getAttribute('data-bs-route-enabled')
  const route = button.getAttribute('data-bs-route')
  const label = toggleRouteModal.querySelector('#toggleRouteModalLabel')
  const info_text = toggleRouteModal.querySelector('#toggleRouteModalInfoText')
  const submit_button = toggleRouteModal.querySelector('#toggleRouteModalSubmitButton')
  const route_id_input = toggleRouteModal.querySelector('#toggleRouteModalRouteID')
  const route_enabled_input = toggleRouteModal.querySelector('#toggleRouteModalRouteEnabled')

  route_id_input.value = route_id
  route_enabled_input.value = route_enabled
  if (route_enabled === "True") {
    info_text.textContent = 'Disable the route "' + route + '"?'
    label.textContent = 'Disable route'
    submit_button.classList.add("btn-danger")
    submit_button.classList.remove("btn-primary")
    submit_button.textContent = 'Disable route'
  } else {
    info_text.textContent = 'Enable the route "' + route + '"?'
    label.textContent = 'Enable route'
    submit_button.classList.add("btn-primary")
    submit_button.classList.remove("btn-danger")
    submit_button.textContent = 'Enable route'
  }
})
