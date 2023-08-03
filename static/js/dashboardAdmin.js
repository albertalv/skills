function showAccounts() {
    document.getElementById('verificar-cuentas').style.display = 'block';
    document.getElementById('revisar-denuncias').style.display = 'none';
    document.getElementById('agregar-modificar-categorias').style.display = 'none';
  }

  function showReports() {
    document.getElementById('verificar-cuentas').style.display = 'none';
    document.getElementById('revisar-denuncias').style.display = 'block';
    document.getElementById('agregar-modificar-categorias').style.display = 'none';
  }

  function showCategories() {
    document.getElementById('verificar-cuentas').style.display = 'none';
    document.getElementById('revisar-denuncias').style.display = 'none';
    document.getElementById('agregar-modificar-categorias').style.display = 'block';
  }

  function viewAccountDetails(accountName) {
    // Lógica para ver los detalles de la cuenta
    console.log('Ver detalles de la cuenta:', accountName);
  }

  function viewReportDetails(username) {
    // Lógica para ver los detalles de la denuncia
    console.log('Ver detalles de la denuncia:', username);
  }

  function editCategory(categoryName) {
    // Lógica para editar la categoría
    console.log('Editar categoría:', categoryName);
  }